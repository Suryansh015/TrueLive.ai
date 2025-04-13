from flask import Flask, request
import os
import subprocess
import requests
import time
import google.generativeai as genai
import logging

app = Flask(__name__)

# ========== CONFIGURATION ==========
ASSEMBLYAI_API_KEY = "nice try"
GEMINI_API_KEY = "nice try"

genai.configure(api_key=GEMINI_API_KEY)
logging.basicConfig(level=logging.INFO)

# ========== AUDIO DOWNLOAD ==========
def download_audio(video_url):
    os.makedirs("temp", exist_ok=True)
    output_file = "temp/audio.mp3"
    try:
        streamlink_cmd = ['streamlink', video_url, 'best', '-O']
        ffmpeg_cmd = ['ffmpeg', '-i', 'pipe:0', '-acodec', 'libmp3lame', '-y', output_file]

        streamlink_proc = subprocess.Popen(streamlink_cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        ffmpeg_proc = subprocess.Popen(ffmpeg_cmd, stdin=streamlink_proc.stdout, stderr=subprocess.DEVNULL)
        streamlink_proc.stdout.close()
        ffmpeg_proc.communicate()

        return output_file
    except Exception as e:
        logging.error(f"Audio download error: {e}")
        return None

# ========== TRANSCRIPTION ==========
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
        time.sleep(2)

# ========== GEMINI VERIFICATION ==========
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
        - Credibility Score
        - Provide urls for sources that confirm or contradict the news. Only urls, no other text.
        - Give Confidence score for each URL by comparing its contents from the summary.
        - Summarize key findings from these sources. And reason why the output states True/False/Partially True.
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logging.error(f"Gemini API error: {e}")
        return " Gemini verification failed."

# ========== ROUTE ==========
@app.route('/', methods=['GET', 'POST'])
def index():
    result = ""
    if request.method == 'POST':
        video_url = request.form.get('video_url')
        result += f"<p> URL received: <strong>{video_url}</strong></p>"

        audio_file = download_audio(video_url)
        if not audio_file:
            result += "<p style='color:red;'> Error downloading audio.</p>"
        else:
            result += "<p> Audio downloaded successfully. Transcribing...</p>"
            try:
                transcript = transcribe_audio(audio_file)
                print(transcript)
                result += f"<hr><h3>AssemblyAI Transcription</h3><pre>{transcript}</pre>"
                result += "<p> Transcription complete. Verifying with Gemini...</p>"
                verification = verify_news_with_gemini(transcript)
                result += f"<hr><h3> Gemini Verification</h3><pre>{verification}</pre>"
            except Exception as e:
                result += f"<p style='color:red;'> Error: {str(e)}</p>"
            
            print(transcript)

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Audio News Verifier</title>
        <style>
            body {{ font-family: Arial, sans-serif; padding: 40px; }}
            input[type="text"] {{ width: 60%; padding: 10px; font-size: 16px; }}
            input[type="submit"] {{ padding: 10px 20px; font-size: 16px; }}
            pre {{ background-color: #f4f4f4; padding: 15px; border-radius: 6px; white-space: pre-wrap; }}
        </style>
    </head>
    <body>
        <h1>🎧 Audio News Verifier</h1>
        <form method="POST">
            <label>Enter YouTube or Instagram Reel URL:</label><br><br>
            <input type="text" name="video_url" required placeholder="https://..." />
            <input type="submit" value="Verify" />
        </form>
        <hr>
        {result}
    </body>
    </html>
    """

# ========== RUN ==========
if __name__ == '__main__':
    app.run(debug=True)