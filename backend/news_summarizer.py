from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS
import os
import subprocess
import yt_dlp
import whisper
from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer
from textblob import TextBlob
from newspaper import Article

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes by default

# Load ASR model
asr_model = whisper.load_model("base")

# Path to the locally downloaded model
local_model_dir = r"C:\\Users\\surya\\Desktop\\_token model 1"

# Load claim model from the local directory
claim_model = pipeline(
    "text-classification",
    model=AutoModelForSequenceClassification.from_pretrained(local_model_dir),
    tokenizer=AutoTokenizer.from_pretrained(local_model_dir)
)

# Utility to convert and resample audio
def convert_and_resample_audio(input_path, output_path="temp_audio.wav", target_sample_rate=16000):
    try:
        result = subprocess.run(
            ["ffmpeg", "-y", "-i", input_path, "-ar", str(target_sample_rate), output_path],
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True
        )
        if result.returncode != 0:
            print(f"FFmpeg error:\n{result.stderr}")
            return None
        return output_path
    except Exception as e:
        print(f"Error converting and resampling audio: {e}")
        return None

# Download YouTube audio
def download_youtube_audio_with_ytdlp(youtube_url, audio_output_path="temp_audio.aac"):
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': audio_output_path,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'aac',
                'preferredquality': '192',
            }],
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])
        return audio_output_path
    except Exception as e:
        print(f"Error downloading audio: {e}")
        return None

# Transcribe audio
def transcribe_audio(audio_path):
    try:
        transcription = asr_model.transcribe(audio_path)
        return transcription['text']
    except Exception as e:
        print(f"Error transcribing audio: {e}")
        return ""

# Check claim
def check_claim(claim):
    try:
        prediction = claim_model(claim)
        result = prediction[0]
        label = result['label']
        score = result['score']
        if label == "LABEL_1":  # Adjust based on your model's labels
            return {"status": "TRUE", "confidence": score}
        else:
            return {"status": "FALSE or UNVERIFIED", "confidence": score}
    except Exception as e:
        print(f"Error checking claim: {e}")
        return {"status": "Error", "confidence": 0}

# Flask route for fact-checking
@app.route("/fact_check", methods=['POST'])
def fact_check():
    data = request.json
    youtube_url = data.get("youtube_url")
    if not youtube_url:
        return jsonify({"error": "YouTube URL is required"}), 400

    # Step 1: Download audio
    audio_path = download_youtube_audio_with_ytdlp(youtube_url)
    if not audio_path:
        return jsonify({"error": "Failed to download audio"}), 500

    # Step 2: Convert and resample audio
    resampled_audio_path = convert_and_resample_audio(audio_path)
    if not resampled_audio_path:
        return jsonify({"error": "Failed to process audio"}), 500

    # Step 3: Transcribe audio
    transcription = transcribe_audio(resampled_audio_path)
    if not transcription:
        return jsonify({"error": "Failed to transcribe audio"}), 500

    # Step 4: Verify claim
    claim_result = check_claim(transcription)

    return jsonify({
        "transcription": transcription,
        "claim_verification": claim_result
    })

# Flask route for summarization and sentiment analysis
@app.route("/summarize", methods=['POST'])
def summarize():
    data = request.get_json()

    url = data.get('url')

    if not url:
        return jsonify({"error": "URL is required"}), 400

    # Process the article
    article = Article(url)
    article.download()
    article.parse()
    article.nlp()

    # Perform sentiment analysis
    analysis = TextBlob(article.text)

    sentiment = {
        "polarity": analysis.polarity,
        "sentiment": "positive" if analysis.polarity > 0 else "negative" if analysis.polarity < 0 else "neutral"
    }

    # Prepare the response
    response = {
        "title": article.title,
        "author": article.authors,
        "publish_date": str(article.publish_date),
        "summary": article.summary,
        "sentiment": sentiment
    }
    
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)




"""
old onli news summarizer flask

from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS
from textblob import TextBlob
from newspaper import Article

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes by default

@app.route('/summarize', methods=['POST'])
def summarize():
    data = request.get_json()

    url = data.get('url')

    if not url:
        return jsonify({"error": "URL is required"}), 400

    # Process the article
    article = Article(url)
    article.download()
    article.parse()
    article.nlp()

    # Perform sentiment analysis
    analysis = TextBlob(article.text)

    sentiment = {
        "polarity": analysis.polarity,
        "sentiment": "positive" if analysis.polarity > 0 else "negative" if analysis.polarity < 0 else "neutral"
    }

    # Prepare the response
    response = {
        "title": article.title,
        "author": article.authors,
        "publish_date": str(article.publish_date),
        "summary": article.summary,
        "sentiment": sentiment
    }

    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
"""