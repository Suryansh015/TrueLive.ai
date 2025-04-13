from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import os 
from newspaper import Article
import nltk
from textblob import TextBlob 
import subprocess
import requests
from urllib.parse import urlparse
import urllib.parse
from dotenv import load_dotenv
import torch
import logging
from googleapiclient.discovery import build
from sentence_transformers import SentenceTransformer, util
from bs4 import BeautifulSoup
from youtube_transcript_api import YouTubeTranscriptApi
import re
import google.generativeai as genai  
import subprocess 
from deepgram import Deepgram
import asyncio
from PIL import Image
import io

nltk.download('punkt')

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
load_dotenv()

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # Limit uploads to 50 MB
ALLOWED_EXTENSIONS = {'mp4'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Paths for models
TOKEN_MODEL_PATH = r"C:\Users\surya\Desktop\Programs\web-projects\truelive.ai\AI models\old models (big ahh)\_token model 1"

# Load Hugging Face model (GEN AI)
device = "cuda" if torch.cuda.is_available() else "cpu"
classifier = pipeline("image-classification", model="umm-maybe/AI-image-detector", device=0 if device == "cuda" else -1)

# Ensure models exist
if not os.path.exists(TOKEN_MODEL_PATH):
    raise FileNotFoundError(f"Token model not found at {TOKEN_MODEL_PATH}.")

# Load models
tokenizer = AutoTokenizer.from_pretrained(TOKEN_MODEL_PATH)
model = AutoModelForSequenceClassification.from_pretrained(TOKEN_MODEL_PATH)
gemini_model = genai.GenerativeModel("gemini-1.5-pro-latest")

# Google Fact Check
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")

# Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Deepgram
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")

# AssemblyAI
ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")

if not DEEPGRAM_API_KEY or not GOOGLE_API_KEY or not GOOGLE_CSE_ID:
    raise ValueError("Missing required API keys. Please check your .env file.")

# List of Known Fake/Unreliable News Sources
FAKE_SOURCES = {
    "beforeitsnews.com", "worldtruth.tv", "naturalnews.com",
    "infowars.com", "breitbart.com", "yournewswire.com",
    "newsbreak.com", "theblaze.com", "conservativetreehouse.com",
    "wnd.com", "thegatewaypundit.com", "thedailybeast.com",
    "newsthump.com", "breakingnewsandreligion.online", 
    "theonion.com"
}

# Social Media Platforms to Check for External Links
SOCIAL_MEDIA_SITES = {"tumblr.com", "reddit.com", "twitter.com", "facebook.com", "tiktok.com"}

# Load Similarity Model for Verification
similarity_model = SentenceTransformer("all-MiniLM-L6-v2")

# stream analysis  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def download_audio(video_url):
    os.makedirs("temp", exist_ok=True)
    output_file = "temp/audio.mp3"
    try:
        streamlink_cmd = ['streamlink', video_url, 'best', '-O']
        ffmpeg_cmd = ['ffmpeg', '-i', 'pipe:0', '-t', '20', '-acodec', 'libmp3lame', '-y', output_file]

        streamlink_proc = subprocess.Popen(streamlink_cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        ffmpeg_proc = subprocess.Popen(ffmpeg_cmd, stdin=streamlink_proc.stdout, stderr=subprocess.DEVNULL)
        streamlink_proc.stdout.close()
        ffmpeg_proc.communicate()

        return output_file
    except Exception as e:
        logging.error(f"Audio download error: {e}")
        return None

def transcribe_audio(audio_file):
    headers = {'authorization': ASSEMBLYAI_API_KEY}
    upload_url = 'https://api.assemblyai.com/v2/upload'

    with open(audio_file, 'rb') as f:
        response = requests.post(upload_url, headers=headers, files={'file': f})
        audio_url = response.json()['upload_url']

    transcript_req = {'audio_url': audio_url, 'language_detection': True}
    transcript_res = requests.post(
        'https://api.assemblyai.com/v2/transcript',
        headers=headers,
        json=transcript_req
    )
    transcript_id = transcript_res.json()['id']

    polling_url = f"https://api.assemblyai.com/v2/transcript/{transcript_id}"
    while True:
        polling_res = requests.get(polling_url, headers=headers)
        status = polling_res.json()['status']
        if status == 'completed':
            return polling_res.json()['text']
        elif status == 'error':
            raise Exception("Transcription failed.")

def verify_news_with_gemini(transcript):
    logging.info("Verifying news authenticity using Gemini API.")
    try:
        model = genai.GenerativeModel("gemini-1.5-pro-latest")
        prompt = f"""
        You are a multilingual fact-checking assistant. Given the following transcription from a news video (which might contain multiple languages), summarize it and check for factual accuracy. Provide a credibility score (0-100), key points, and suggest sources for verification if applicable.

        Transcript:
        {transcript} 

        Respond in markdown with sections:
        - Verification: True/False/Partially True ; only single word for this section
        - Summary 
        - Key Points (from the summary, as bullet list)
        - Credibility Score
        - Provide urls for 3 sources that confirm or contradict the news. Only urls, no other text.
        - Give Confidence score for each URL by comparing its contents from the summary.
        - Summarize key findings from these sources. And reason why the output states True/False/Partially True.
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logging.error(f"Gemini API error: {e}")
        return " Gemini verification failed."

# video verification ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def extract_video_id(url):
    query = urllib.parse.urlparse(url)
    if query.hostname == 'youtu.be':
        return query.path[1:]
    if query.hostname in ('www.youtube.com', 'youtube.com'):
        if query.path == '/watch':
            return urllib.parse.parse_qs(query.query)['v'][0]
        if query.path.startswith('/embed/') or query.path.startswith('/v/'):
            return query.path.split('/')[2]
        if query.path.startswith('/shorts/'):  # ✅ Handle YouTube Shorts
            return query.path.split('/')[2]
    return None

def get_transcript(video_id):
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

        # ✅ Try to get Hindi and English transcript
        try:
            transcript = transcript_list.find_transcript(['hi', 'en'])  # 'hi' for Hindi, 'en' for English
        except:
            return None

        transcript_text = transcript.fetch()
        return ' '.join([d['text'] for d in transcript_text])
    
    except Exception:
        return None

def summarize_text(transcript):
    """✅ Use Gemini to summarize the transcript"""
    try:
        model = genai.GenerativeModel("gemini-1.5-pro-latest")
        prompt = f"Summarize the following transcript in a concise and clear format:\n\n{transcript}"
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception:
        return "⚠️ Error in summarization."

def extract_key_points_video(transcript):
    try:
        model = genai.GenerativeModel("gemini-1.5-pro-latest")
        prompt = f"Extract the key points from the following transcript:\n\n{transcript}"
        response = model.generate_content(prompt)
        return response.text.strip().split("\n")
    except Exception:
        return ["⚠️ Error extracting key points."]

""" key points extract without llm
def extract_key_points_video(summary):
    sentences = re.split(r'[.!?]+', summary)
    key_points = [s.strip() for s in sentences if len(s.strip()) > 20]
    return key_points
"""

def verify_news_with_gemini_video(summary):
    """✅ Verify news using Gemini and fetch sources with credibility scores."""
    try:
        model = genai.GenerativeModel("gemini-1.5-pro-latest")
        prompt = f"""
        Verify the authenticity of the following news.  
        - Provide a truthfulness rating (True, Partially True, False).  
        - List at least **two sources with URLs** that confirm or contradict this news.  
        - Assign a **credibility score (1-10)** to each source based on reliability.  
        - Summarize key findings from these sources.  

        **News Summary:** {summary}
        """
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception:
        return "⚠️ Error in verification."
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
""" news summarizer removed
def summarize_article(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        article.nlp()
        analysis = TextBlob(article.text)
        return {
            "title": article.title,
            "author": article.authors,
            "publish_date": str(article.publish_date),
            "summary": article.summary,
            "sentiment": {
                "polarity": analysis.polarity,
                "sentiment": "positive" if analysis.polarity > 0 else "negative" if analysis.polarity < 0 else "neutral"
            }
        }
    except Exception as e:
        print(f"Article processing error: {e}")
        return {"error": f"Article processing error: {e}"}
"""
# article verification ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def extract_domain(url):
    try:
        parsed_url = urlparse(url)
        return parsed_url.netloc.replace("www.", "")
    except Exception:
        return None

def extract_external_links(social_media_url):
    try:
        response = requests.get(social_media_url, timeout=5)
        soup = BeautifulSoup(response.text, "html.parser")
        links = [a["href"] for a in soup.find_all("a", href=True)]
        return links
    except Exception:
        return []

def extract_claims(article_text, article_title, top_k=3, confidence_threshold=0.6):
    claims_to_check = [article_title] + article_text.split(". ")
    valid_claims = []

    for claim in claims_to_check:
        if len(claim.strip()) < 10:
            continue

        inputs = tokenizer(claim, return_tensors="pt", truncation=True, padding=True)
        with torch.no_grad():
            outputs = model(**inputs)
            probabilities = torch.nn.functional.softmax(outputs.logits, dim=1)

        confidence = probabilities[0, 1].item()
        if confidence >= confidence_threshold:
            valid_claims.append((claim, confidence))

    return sorted(valid_claims, key=lambda x: x[1], reverse=True)[:top_k]

def verify_claim_with_search(claim_text, input_article_url):
    input_domain = extract_domain(input_article_url)
    service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY)
    
    try:
        response = service.cse().list(q=claim_text, cx=GOOGLE_CSE_ID, num=5).execute()
        if "items" not in response:
            return "No sources found", 0.0, False

        search_results = response["items"]
        valid_sources = []
        best_match_score = 0.0

        for result in search_results:
            source_url = result["link"]
            source_domain = extract_domain(source_url)
            source_snippet = result["snippet"]

            if source_domain == input_domain or source_domain in FAKE_SOURCES:
                continue

            # Check if it's a social media link
            if source_domain in SOCIAL_MEDIA_SITES:
                logging.info(f"Social media post detected: {source_url}")
                external_links = extract_external_links(source_url)

                # Search for a reliable external link within the social media post
                reliable_link_found = False
                for sub_link in external_links:
                    sub_domain = extract_domain(sub_link)
                    if sub_domain not in FAKE_SOURCES and sub_domain != input_domain:
                        logging.info(f"Found reliable external link: {sub_link}")
                        source_url = sub_link
                        source_domain = sub_domain
                        reliable_link_found = True
                        break

                if not reliable_link_found:
                    logging.info(f"No reliable sources in social media post: {source_url}")
                    continue

            claim_embedding = similarity_model.encode(claim_text, convert_to_tensor=True)
            source_embedding = similarity_model.encode(source_snippet, convert_to_tensor=True)
            similarity_score = util.pytorch_cos_sim(claim_embedding, source_embedding).item()

            valid_sources.append((source_url, similarity_score))
            best_match_score = max(best_match_score, similarity_score)

        if not valid_sources:
            return "No reliable sources", 0.0, False

        best_source, best_confidence = max(valid_sources, key=lambda x: x[1])
        is_true = best_confidence > 0.5
        return best_source, best_confidence, is_true

    except Exception as e:
        return "Search Error", 0.0, False
# REELS ANALYSIS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def download_audio_insta(instagram_url, output_dir="downloads"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    command = [
        "yt-dlp",
        "-f", "bestaudio",
        "--extract-audio",
        "--audio-format", "mp3",
        "-o", os.path.join(output_dir, "audio.%(ext)s"),
        instagram_url
    ]

    try:
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        logging.error(f"yt-dlp failed: {e}")
        return None

    for file in os.listdir(output_dir):
        if file.endswith(".mp3"):
            return os.path.join(output_dir, file)
    return None

def transcribe_with_assembly_insta(file_path):
    headers = {'authorization': ASSEMBLYAI_API_KEY}

    with open(file_path, 'rb') as f:
        response = requests.post('https://api.assemblyai.com/v2/upload', headers=headers, data=f)
        if response.status_code != 200:
            raise Exception("Upload failed.")
        audio_url = response.json()['upload_url']

    transcript_response = requests.post('https://api.assemblyai.com/v2/transcript', json={'audio_url': audio_url}, headers=headers)
    transcript_id = transcript_response.json()['id']

    polling_url = f'https://api.assemblyai.com/v2/transcript/{transcript_id}'
    while True:
        polling_response = requests.get(polling_url, headers=headers).json()
        if polling_response['status'] == 'completed':
            return polling_response['text']
        elif polling_response['status'] == 'error':
            raise Exception(f"Transcription error: {polling_response['error']}")

def verify_news_with_gemini_insta(summary):
    try:
        prompt = f"""
        Verify the authenticity of the following news.  
        - Provide a truthfulness rating (e.g., True, Partially True, False).  
        - List at least **two sources with URLs** that confirm or contradict this news.  
        - Assign a **credibility score (1-10)** to each source based on reliability.  
        - Summarize key findings from these sources.  

        **News Summary:** {summary}
        """
        response = gemini_model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        logging.error(f"Error in Gemini news verification: {e}")
        return f"⚠️ Error in verification: {str(e)}"

# routes ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
@app.route('/verify_article', methods=['POST'])
def verify_article_route():
    data = request.json
    url = data.get("url")
    if not url:
        return jsonify({"error": "URL is required"}), 400

    try:
        # Get article content
        article = Article(url)
        article.download()
        article.parse()
        article.nlp()
        
        # Extract claims
        claims = extract_claims(article.text, article.title)
        if not claims:
            return jsonify({"error": "No claims could be extracted"}), 400

        # Get the best claim
        best_claim = claims[0][0]
        
        # Verify using Google search
        best_source, confidence_score, is_true = verify_claim_with_search(best_claim, url)
        
        # Prepare response
        verification_result = {
            "status": "Verified" if is_true else "Unverified",
            "confidence": round(confidence_score * 100, 2),
            "source": best_source
        }

        # Get article summary
        analysis = TextBlob(article.text)
        article_summary = {
            "title": article.title,
            "author": article.authors,
            "publish_date": str(article.publish_date),
            "summary": article.summary,
            "sentiment": {
                "polarity": analysis.polarity,
                "sentiment": "positive" if analysis.polarity > 0 else "negative" if analysis.polarity < 0 else "neutral"
            }
        }

        return jsonify({
            "article": article_summary,
            "claim_verification": verification_result,
            "claims": [{"text": claim, "confidence": conf} for claim, conf in claims]
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/videoanalyze", methods=["POST"])
def analyze_video():
    try:
        data = request.get_json()
        url = data.get("url")

        if not url:
            return jsonify({"error": "No YouTube URL provided"}), 400

        video_id = extract_video_id(url)
        if not video_id:
            return jsonify({"error": "Invalid YouTube URL"}), 400

        transcript = get_transcript(video_id)
        if not transcript:
            return jsonify({"error": "No transcript available for this video"}), 400

        summary = summarize_text(transcript)
        key_points = extract_key_points_video(transcript)
        verification_result = verify_news_with_gemini_video(summary)

        return jsonify({
            "summary": summary,
            "key_points": key_points,
            "verification_result": verification_result,
            "video_id": video_id
        })
    
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500
    
""" news summarizer removed
@app.route('/summarize', methods=['POST'])
def summarize_route():
    data = request.json
    url = data.get("url")
    if not url:
        return jsonify({"error": "URL is required"}), 400

    summary = summarize_article(url)
    return jsonify(summary)
"""

@app.route('/analyze_stream', methods=['POST'])
def analyze_stream():
    try:
        data = request.get_json()
        video_url = data.get('url')

        # Step 1: Download audio
        audio_file = download_audio(video_url)
        if not audio_file:
            return jsonify({'error': 'Audio download failed.'}), 500

        # Step 2: Transcribe
        transcript = transcribe_audio(audio_file)

        # Step 3: Verify using Gemini
        verification = verify_news_with_gemini(transcript)

        # Optional: Extract key points from Gemini output if needed (basic example)
        key_points = []
        if verification:
            import re
            match = re.search(r"(?<=- Summary\s)(.*?)(?=\n- Credibility|$)", verification, re.DOTALL)
            if match:
                summary_text = match.group(1).strip()
                key_points = [line.strip("- ").strip() for line in summary_text.split("\n") if line.strip()]

        return jsonify({
            'transcript': transcript,
            'verification': verification,
            'key_points': key_points
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/genAI", methods=["POST"])
def genAI_Det():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    try:
        # Convert image to PIL format
        image = Image.open(io.BytesIO(file.read())).convert("RGB")

        # Run the model prediction
        result = classifier(image)[0]
        prediction = result["label"]
        confidence = result["score"] * 100  # Convert to percentage

        return jsonify({
            "status": "success",
            "prediction": prediction,
            "confidence": confidence
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/articlekeyword', methods=['POST'])
def article_keyword():
    data = request.get_json()
    user_input = data.get("news_input")

    if not user_input:
        return jsonify({"error": "Missing 'news_input' field"}), 400

    prompt = f"""
    I have a statement: "{user_input}"

    Please tell me:
    1. Is it Verified, Unverified, or Partially Verified?
    2. Give a credibility score out of 100.

    Format your response exactly like this (no extra words):
    Verification: <status>
    Credibility Score: <score>/100
    """

    try:
        response = gemini_model.generate_content(prompt)
        raw_output = response.text
        print("Gemini Response:\n", raw_output)  # Debug log

        # Use regex to extract data
        verification_match = re.search(r"Verification:\s*(.*)", raw_output, re.IGNORECASE)
        score_match = re.search(r"Credibility Score:\s*(\d+)", raw_output, re.IGNORECASE)

        verification = verification_match.group(1).strip() if verification_match else "Not Available"
        credibility_score = score_match.group(1).strip() if score_match else "0"

        return jsonify({
            "verification": verification,
            "credibility_score": credibility_score
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/analyze_reels", methods=["POST"])
def analyze_reels():
    data = request.get_json()
    if not data or "url" not in data:
        return jsonify({"error": "Missing 'url' in request"}), 400

    url = data["url"]
    try:
        audio_path = download_audio_insta(url)
        if not audio_path:
            raise Exception("Audio file not found after download.")

        transcript = transcribe_with_assembly_insta(audio_path)
        verification = verify_news_with_gemini_insta(transcript)

        return jsonify({
            "transcript": transcript,
            "verification": verification
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)