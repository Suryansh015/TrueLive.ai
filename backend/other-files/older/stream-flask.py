from flask import Flask, request, jsonify
from flask_cors import CORS
import re
import urllib.parse
import os
import subprocess 
from deepgram import Deepgram
import google.generativeai as genai
import asyncio
from dotenv import load_dotenv

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
# Load environment variables
load_dotenv() 

# Configure API keys
DEEPGRAM_API_KEY = "nice try"
GEMINI_API_KEY = "nice try"

if not DEEPGRAM_API_KEY or not GEMINI_API_KEY:
    raise ValueError("Missing required API keys. Please check your .env file.")

genai.configure(api_key=GEMINI_API_KEY)

def extract_video_id(url):
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

def extract_key_points(text):
    sentences = re.split(r'[.!?]+', text)
    return [s.strip() for s in sentences if len(s.strip()) > 20]

def verify_news_with_gemini(summary):
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

@app.route('/analyze_stream', methods=['POST'])
def analyze_stream():
    data = request.get_json()
    url = data.get('url')
    
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    video_id = extract_video_id(url)
    if not video_id:
        return jsonify({"error": "Invalid YouTube URL"}), 400

    try:
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        audio_path = download_audio(video_url)
        if not audio_path:
            return jsonify({"error": "Audio download failed"}), 500
        
        transcript = asyncio.run(get_live_transcript(audio_path))
        key_points = extract_key_points(transcript)
        verification = verify_news_with_gemini(transcript)

        os.remove(audio_path)

        return jsonify({
            "transcript": transcript,
            "key_points": key_points,
            "verification": verification
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
