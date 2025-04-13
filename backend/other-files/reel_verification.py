from flask import Flask, request, render_template_string, jsonify
import subprocess
import os
import requests
import time
import logging
import google.generativeai as genai
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Configure your API keys
ASSEMBLY_API_KEY = "nice try"
genai.configure(api_key="nice try")
gemini_model = genai.GenerativeModel("gemini-1.5-pro-latest")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Instagram Audio Verifier</title>
    <style>
        body { font-family: Arial; margin: 40px; background: #f4f4f4; }
        h1 { color: #333; }
        input[type=text], button {
            width: 100%%; padding: 10px; margin-top: 10px;
        }
        button {
            background-color: #4CAF50; color: white; border: none; cursor: pointer;
        }
        .results { margin-top: 30px; padding: 20px; background: #fff; border-radius: 8px; }
        .error { color: red; }
    </style>
</head>
<body>
    <h1>Instagram Reel Audio Verification</h1>
    <form method="POST">
        <input type="text" name="url" placeholder="Paste Instagram Reel URL" required>
        <button type="submit">Submit</button>
    </form>

    {% if summary %}
    <div class="results">
        <h2>🎧 Transcription</h2>
        <p>{{ summary }}</p>

        <h2>✅ Gemini Verification</h2>
        <pre>{{ verification }}</pre>
    </div>
    {% elif error %}
    <p class="error">⚠️ {{ error }}</p>
    {% endif %}
</body>
</html>
"""

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
    headers = {'authorization': ASSEMBLY_API_KEY}

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
        time.sleep(3)

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

@app.route("/", methods=["GET", "POST"])
def index():
    summary = ""
    verification = ""
    error = ""

    if request.method == "POST":
        url = request.form.get("url")
        try:
            audio_path = download_audio_insta(url)
            if not audio_path:
                raise Exception("Audio file not found after download.")
            summary = transcribe_with_assembly_insta(audio_path)
            verification = verify_news_with_gemini_insta(summary)
        except Exception as e:
            error = str(e)

    return render_template_string(HTML_TEMPLATE, summary=summary, verification=verification, error=error)

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


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
