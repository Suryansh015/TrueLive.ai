from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import AutoTokenizer
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
CLAIM_ONNX_MODEL_PATH = r"C:\Users\surya\Desktop\Programs\ReactJS\tthackathon-project-site\AI models\distilbert_local_model_quantized.onnx"
VOSK_MODEL_PATH = r"C:\Users\surya\Desktop\Programs\ReactJS\tthackathon-project-site\AI models\vosk-model-small-en-in-0.4"

# Ensure models exist
if not os.path.exists(VOSK_MODEL_PATH):
    raise FileNotFoundError(f"Vosk model not found at {VOSK_MODEL_PATH}.")
if not os.path.exists(CLAIM_ONNX_MODEL_PATH):
    raise FileNotFoundError(f"ONNX model not found at {CLAIM_ONNX_MODEL_PATH}.")

# Load models
vosk_model = VoskModel(VOSK_MODEL_PATH)
tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")
distilbert_session = ort.InferenceSession(CLAIM_ONNX_MODEL_PATH)

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
    

@app.route('/verify_article', methods=['POST'])
def verify_article_route():
    data = request.json
    url = data.get("url")
    if not url:
        return jsonify({"error": "URL is required"}), 400

    article = summarize_article(url)
    claim_verification = check_claim(f"{article.get('title')} {article.get('summary')}")
    return jsonify({
        "article": article, 
        "claim_verification": claim_verification
    })

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



# Routes remain the same as in the previous code snippet

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)


