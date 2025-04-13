from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from transformers import pipeline
import re
import urllib.parse
import google.generativeai as genai  
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
genai.configure(api_key="nice try")

def extract_video_id(url):
    query = urllib.parse.urlparse(url)
    if query.hostname == 'youtu.be':
        return query.path[1:]
    if query.hostname in ('www.youtube.com', 'youtube.com'):
        if query.path == '/watch':
            return urllib.parse.parse_qs(query.query)['v'][0]
        if query.path[:7] == '/embed/':
            return query.path.split('/')[2]
        if query.path[:3] == '/v/':
            return query.path.split('/')[2]
    return None

def get_transcript(video_id):
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = ' '.join([d['text'] for d in transcript_list])
        return transcript
    except Exception as e:
        return str(e)

def summarize_text(text, max_length=150, min_length=50):
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    max_chunk_size = 1024
    chunks = [text[i:i + max_chunk_size] for i in range(0, len(text), max_chunk_size)]
    summaries = [summarizer(chunk, max_length=max_length, min_length=min_length, do_sample=False)[0]['summary_text'] for chunk in chunks]
    return ' '.join(summaries)

def extract_key_points(summary):
    sentences = re.split(r'[.!?]+', summary)
    key_points = [s.strip() for s in sentences if len(s.strip()) > 20]
    return key_points

def verify_news_with_gemini(summary):
    try:
        model = genai.GenerativeModel("gemini-1.5-pro-latest")
        prompt = f"""
        Verify the authenticity of the following news.  
        - Provide a truthfulness rating (e.g., True, Partially True, False).  
        - List at least **two sources with URLs** that confirm or contradict this news.  
        - Assign a **credibility score (1-10)** to each source based on reliability.  
        - Summarize key findings from these sources.  

        **News Summary:** {summary}
        """
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return str(e)

# ✅ API for YouTube Video Analysis
@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        video_url = data.get('url')

        video_id = extract_video_id(video_url)
        if not video_id:
            return jsonify({"error": "Invalid YouTube URL"}), 400

        transcript = get_transcript(video_id)
        if transcript.startswith("Error"):
            return jsonify({"error": transcript}), 500

        summary = summarize_text(transcript)
        key_points = extract_key_points(summary)
        verification_result = verify_news_with_gemini(summary)

        return jsonify({
            "summary": summary,
            "key_points": key_points,
            "verification_result": verification_result,
            "video_id": video_id
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ Error Handlers
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not Found"}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal Server Error"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
