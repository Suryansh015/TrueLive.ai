from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
import urllib.parse
import google.generativeai as genai  
from flask_cors import CORS

# ✅ Configure Gemini API Key
genai.configure(api_key="AIzaSyAZ-VSjhpn7INnb9ziyK5LRZBG8B1M8xD8")  # Replace with your actual API key

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
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
    """✅ Extract key points using Gemini"""
    try:
        model = genai.GenerativeModel("gemini-1.5-pro-latest")
        prompt = f"Extract the key points from the following transcript:\n\n{transcript}"
        response = model.generate_content(prompt)
        return response.text.strip().split("\n")
    except Exception:
        return ["⚠️ Error extracting key points."]

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

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
