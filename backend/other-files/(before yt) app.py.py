from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from vosk import Model as VoskModel, KaldiRecognizer
import wave
import os
import json
from newspaper import Article
import nltk
from textblob import TextBlob
from werkzeug.utils import secure_filename
import subprocess
import numpy as np
from scipy.special import softmax
import onnxruntime as ort
import requests
from urllib.parse import quote, urlparse
from dotenv import load_dotenv
import torch
import logging
from googleapiclient.discovery import build
from sentence_transformers import SentenceTransformer, util
from bs4 import BeautifulSoup

# Download necessary NLTK data
nltk.download('punkt')

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Configurations
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # Limit uploads to 50 MB
ALLOWED_EXTENSIONS = {'mp4'}

# Helper function to check file type
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Paths for models
CLAIM_ONNX_MODEL_PATH = r"C:\Users\surya\Desktop\Programs\web-projects\truelive.ai\AI models\distilbert_local_model_quantized.onnx"
VOSK_MODEL_PATH = r"C:\Users\surya\Desktop\Programs\web-projects\truelive.ai\AI models\old models (big ahh)\vosk-model-en-in-0.5"
TOKEN_MODEL_PATH = r"C:\Users\surya\Desktop\Programs\web-projects\truelive.ai\AI models\old models (big ahh)\_token model 1"

# Ensure models exist
if not os.path.exists(VOSK_MODEL_PATH):
    raise FileNotFoundError(f"Vosk model not found at {VOSK_MODEL_PATH}.")
if not os.path.exists(CLAIM_ONNX_MODEL_PATH):
    raise FileNotFoundError(f"ONNX model not found at {CLAIM_ONNX_MODEL_PATH}.")
if not os.path.exists(TOKEN_MODEL_PATH):
    raise FileNotFoundError(f"Token model not found at {TOKEN_MODEL_PATH}.")

# Load models
vosk_model = VoskModel(VOSK_MODEL_PATH)
tokenizer = AutoTokenizer.from_pretrained(TOKEN_MODEL_PATH)
model = AutoModelForSequenceClassification.from_pretrained(TOKEN_MODEL_PATH)
distilbert_session = ort.InferenceSession(CLAIM_ONNX_MODEL_PATH)

# Google API Credentials
GOOGLE_API_KEY = "AIzaSyBiUNAC2c10VcZ4c2CzY1jnJrwubIEcQaE"
GOOGLE_CSE_ID = "44e4a7efcf2964d35"

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

# Extract and resample audio from video
def extract_and_resample_audio(video_path, output_audio_path="temp_audio.wav", target_sample_rate=16000):
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-i", video_path, "-ar", str(target_sample_rate), "-ac", "1", "-sample_fmt", "s16", output_audio_path],
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True
        )
        return output_audio_path
    except Exception as e:
        return None

# Transcribe audio using Vosk
def transcribe_audio_vosk(audio_path):
    try:
        with wave.open(audio_path, "rb") as wf:
            recognizer = KaldiRecognizer(vosk_model, wf.getframerate())
            recognizer.SetWords(True)

            transcription = ""
            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    transcription += result.get("text", "") + " "

            final_result = json.loads(recognizer.FinalResult())
            transcription += final_result.get("text", "")
            return transcription.strip()
    except Exception as e:
        return ""

# Function to verify claims using DistilBERT ONNX model
def check_claim(claim):
    try:
        inputs = tokenizer(claim, return_tensors="pt", truncation=True, padding=True, max_length=512)
        input_ids = inputs["input_ids"].numpy()
        attention_mask = inputs["attention_mask"].numpy()

        # Run inference
        input_names = [i.name for i in distilbert_session.get_inputs()]
        output_name = distilbert_session.get_outputs()[0].name
        outputs = distilbert_session.run([output_name], {
            input_names[0]: input_ids,
            input_names[1]: attention_mask
        })

        logits = outputs[0]
        predicted_class_id = np.argmax(logits, axis=1).item()
        confidence_score = float(np.max(softmax(logits), axis=1).item()) * 100

        return {
            "status": "Verified" if predicted_class_id == 1 else "Unverified",
            "confidence": round(confidence_score, 2)
        }
    except Exception as e:
        return {
            "status": "Error",
            "confidence": 0
        }

# Function to summarize an article
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

def extract_domain(url):
    try:
        parsed_url = urlparse(url)
        return parsed_url.netloc.replace("www.", "")
    except Exception:
        return None

# Extract External Links from Social Media
def extract_external_links(social_media_url):
    try:
        response = requests.get(social_media_url, timeout=5)
        soup = BeautifulSoup(response.text, "html.parser")
        links = [a["href"] for a in soup.find_all("a", href=True)]
        return links
    except Exception:
        return []

# Extract Claims
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

# Verify Claim with Search
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
        is_true = best_confidence > 0.6
        return best_source, best_confidence, is_true

    except Exception as e:
        return "Search Error", 0.0, False

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

@app.route('/', methods=['GET', 'POST'])
def video_verification():
    if request.method == 'GET':
        return jsonify({"message": "Welcome to the video verification API. Use POST to upload a video file for processing."})
    
    if 'video' not in request.files:
        return jsonify({"error": "No file uploaded."}), 400

    video_file = request.files['video']
    if not allowed_file(video_file.filename):
        return jsonify({"error": "Invalid file type."}), 400

    filename = secure_filename(video_file.filename)
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    video_file.save(video_path)

    audio_path = extract_and_resample_audio(video_path)
    if not audio_path:
        return jsonify({"error": "Failed to extract audio."}), 500

    transcription = transcribe_audio_vosk(audio_path)
    if not transcription:
        return jsonify({"error": "Failed to transcribe audio."}), 500

    claim_verification = check_claim(transcription)
    return jsonify({
        "transcription": transcription, 
        "claim_verification": claim_verification
    })

@app.route('/summarize', methods=['POST'])
def summarize_route():
    data = request.json
    url = data.get("url")
    if not url:
        return jsonify({"error": "URL is required"}), 400

    summary = summarize_article(url)
    return jsonify(summary)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)