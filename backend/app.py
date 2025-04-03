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

# Google fact check API Credentials
GOOGLE_API_KEY = "AIzaSyBiUNAC2c10VcZ4c2CzY1jnJrwubIEcQaE"
GOOGLE_CSE_ID = "44e4a7efcf2964d35"

# gemini keys
genai.configure(api_key="AIzaSyCpdg6cbxBmDCPPPGpF6kq7x4wnwfsio6Y")

# Deepgram Key
DEEPGRAM_API_KEY = '3276b4bd5a8a2da34ceba6b97dd3b04cc2bac249'

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
def extract_stream_id(url):
    try:
        query = urllib.parse.urlparse(url)
        if query.hostname == 'youtu.be':
            return query.path[1:]
        if query.hostname in ('www.youtube.com', 'youtube.com'):
            if query.path == '/watch':
                return urllib.parse.parse_qs(query.query).get('v', [None])[0]
            if query.path.startswith(('/embed/', '/v/')):
                return query.path.split('/')[2]
        return None
    except Exception as e:
        return str(e)

def download_audio(video_url):
    try:
        os.makedirs('temp', exist_ok=True)
        output_file = 'temp/audio.mp3'

        streamlink_command = ['streamlink', video_url, 'best', '-O']
        ffmpeg_command = [
            'ffmpeg', '-i', 'pipe:0', '-t', '20',
            '-acodec', 'libmp3lame', '-y', output_file
        ]

        streamlink_process = subprocess.Popen(
            streamlink_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        ffmpeg_process = subprocess.Popen(
            ffmpeg_command, stdin=streamlink_process.stdout, stderr=subprocess.PIPE
        )
        streamlink_process.stdout.close()
        _, ffmpeg_stderr = ffmpeg_process.communicate()

        if ffmpeg_process.returncode != 0:
            raise Exception(f"FFmpeg error: {ffmpeg_stderr.decode()}")

        return output_file if os.path.exists(output_file) else None
    except Exception as e:
        return str(e)

async def get_live_transcript(audio_path):
    try:
        dg_client = Deepgram(DEEPGRAM_API_KEY)
        with open(audio_path, 'rb') as audio:
            source = {'buffer': audio, 'mimetype': 'audio/mp3'}
            response = await dg_client.transcription.prerecorded(
                source,
                {'punctuate': True, 'language': 'en', 'model': 'general'}
            )
        return response['results']['channels'][0]['alternatives'][0]['transcript']
    except Exception as e:
        return str(e)

def extract_key_points_stream(text):
    sentences = re.split(r'[.!?]+', text)
    return [s.strip() for s in sentences if len(s.strip()) > 20]

def verify_news_with_gemini_stream(summary):
    try:
        model = genai.GenerativeModel('gemini-1.5-pro-latest')
        prompt = f"""
        Analyze this news livestream summary for authenticity:
        
        {summary}
        
        Please provide:
        1. Truthfulness rating (True/Partially True/False)
        2. Two reliable sources with URLs
        3. Credibility score (1-10) for each source
        4. Key findings summary
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return str(e)

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
    data = request.get_json()
    url = data.get('url')
    
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    video_id = extract_stream_id(url)
    if not video_id:
        return jsonify({"error": "Invalid YouTube URL"}), 400

    try:
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        audio_path = download_audio(video_url)
        if not audio_path:
            return jsonify({"error": "Audio download failed"}), 500
        
        transcript = asyncio.run(get_live_transcript(audio_path))
        key_points = extract_key_points_stream(transcript)
        verification = verify_news_with_gemini_stream(transcript)

        os.remove(audio_path)

        return jsonify({
            "transcript": transcript,
            "key_points": key_points,
            "verification": verification
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)