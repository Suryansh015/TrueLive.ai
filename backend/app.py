from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline
from vosk import Model as VoskModel, KaldiRecognizer
import wave
import ffmpeg
import os
import json
from newspaper3k import Article
import nltk
from textblob import TextBlob
from werkzeug.utils import secure_filename
import subprocess

nltk.download('movie_reviews')
nltk.download('punkt')

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # Limit uploads to 50 MB

# Allowed file extensions
ALLOWED_EXTENSIONS = {'mp4'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Load models
CLAIM_MODEL_PATH = r"path_to_your_ba-claim/distilbert"
VOSK_MODEL_PATH = r"path_to_vosk_asr_model"


if not os.path.exists(VOSK_MODEL_PATH):
    raise FileNotFoundError(f"Vosk model not found at {VOSK_MODEL_PATH}.")
if not os.path.exists(CLAIM_MODEL_PATH):
    raise FileNotFoundError(f"Transformer model not found at {CLAIM_MODEL_PATH}.")

vosk_model = VoskModel(VOSK_MODEL_PATH)
tokenizer = AutoTokenizer.from_pretrained(CLAIM_MODEL_PATH)
claim_model = AutoModelForSequenceClassification.from_pretrained(CLAIM_MODEL_PATH)
claim_pipeline = pipeline("text-classification", model=claim_model, tokenizer=tokenizer)


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

def check_claim(claim):
    try:
        inputs = tokenizer(claim, return_tensors="pt", truncation=True, padding=True, max_length=512)
        outputs = claim_model(**inputs)
        logits = outputs.logits
        predicted_class_id = logits.argmax().item()
        confidence_score = logits.softmax(dim=1).max().item()

        if predicted_class_id == 1:
            return f"TRUE with confidence {confidence_score:.2f}"
        else:
            return f"FALSE/UNVERIFIED with confidence {confidence_score:.2f}"
    except Exception as e:
        return "Error in claim verification."



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

# Routes


@app.route('/', methods=['GET', 'POST'])
def video_verification():
    if request.method == 'GET':
        return jsonify({"message": "Welcome to the video verification API. Use POST to upload a video file for processing."})
    
    result = None
    transcription = None
    error_message = None
    try:
        if 'video' not in request.files:
            return jsonify({"error": "No file uploaded."}), 400

        video_file = request.files['video']
        if video_file.filename == '':
            return jsonify({"error": "No selected file."}), 400
        if not allowed_file(video_file.filename):
            return jsonify({"error": "File type not allowed."}), 400

        # Save the file securely
        filename = secure_filename(video_file.filename)
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        video_file.save(video_path)

        # Extract and resample audio
        audio_path = extract_and_resample_audio(video_path)
        if not audio_path:
            return jsonify({"error": "Failed to process audio"}), 500

        #  Transcribe the audio
        transcription = transcribe_audio_vosk(audio_path)
        if not transcription:
            return jsonify({"error": "Failed to transcribe audio"}), 500

        #  Verify claims
        result = check_claim(transcription)
        return jsonify({"transcription": transcription, "claim_verification": result})
    except Exception as e:
        print(f"Error processing video: {str(e)}")
        return jsonify({"error": f"Error processing video: {str(e)}"}), 500



@app.route('/verify_article', methods=['POST'])
def verify_article_route():
    try:
        data = request.json
        url = data.get("url")
        if not url:
            return jsonify({"error": "URL is required"}), 400

        article = summarize_article(url)
        claim_verification = check_claim(f"{article.get('title')} {article.get('summary')}")
        return jsonify({"article": article, "claim_verification": claim_verification})
    except Exception as e:
        print(f"Error in verify_article_route: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/summarize', methods=['POST'])
def summarize_route():
    try:
        data = request.json
        url = data.get("url")
        if not url:
            return jsonify({"error": "URL is required"}), 400

        summary = summarize_article(url)
        return jsonify(summary)
    except Exception as e:
        print(f"Error in summarize_route: {e}")
        return jsonify({"error": str(e)}), 500

@app.errorhandler(Exception)
def handle_general_error(e):
    print(f"Unhandled error: {e}")
    return jsonify({"error": "An unexpected error occurred."}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
