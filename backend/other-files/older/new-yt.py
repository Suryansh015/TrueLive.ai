import os
import logging
import re
import urllib.parse
from flask import Flask, request, render_template_string
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai
from sentence_transformers import SentenceTransformer, util
import requests
from bs4 import BeautifulSoup

# ---------------------------
# 🔧 Setup logging
# ---------------------------
logging.basicConfig(level=logging.INFO)

# ---------------------------
# ✅ Load Sentence Similarity Model
# ---------------------------
sentence_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# ---------------------------
# ✅ Setup Gemini API
# ---------------------------
genai.configure(api_key="nice try")
gemini_model = genai.GenerativeModel("gemini-1.5-pro-latest")

# ---------------------------
# 🚀 Flask app
# ---------------------------
app = Flask(__name__)

# ---------------------------
# 🔍 Helper: Extract YouTube video ID
# ---------------------------
def extract_video_id(url):
    query = urllib.parse.urlparse(url)
    if query.hostname == 'youtu.be':
        return query.path[1:]
    if query.hostname in ('www.youtube.com', 'youtube.com'):
        if query.path == '/watch':
            return urllib.parse.parse_qs(query.query)['v'][0]
        if query.path.startswith(('/embed/', '/v/')):
            return query.path.split('/')[2]
    return None

# ---------------------------
# 📜 Helper: Get transcript from YouTube
# ---------------------------
def get_transcript(video_id):
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        return ' '.join([d['text'] for d in transcript_list])
    except Exception as e:
        return f"⚠ Error: {str(e)}"

# ---------------------------
# 📝 Generate summary using Gemini
# ---------------------------
def generate_summary(transcript):
    try:
        prompt = f"""
        Please provide a concise and accurate summary (around 200-300 words) of the following YouTube transcript.
        Focus on the main claims, arguments, and key points made in the video:
        
        {transcript}
        """
        response = gemini_model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠ Error generating summary: {str(e)}"

# ---------------------------
# 🌐 Get article content from URL
# ---------------------------
def get_article_content(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'footer', 'iframe', 'img']):
            element.decompose()
        
        # Get text from main content areas
        article_text = ' '.join([p.get_text() for p in soup.find_all('p')])
        return article_text[:5000]  # Limit to first 5000 chars to avoid too long text
    except Exception as e:
        return f"⚠ Error fetching article: {str(e)}"

# ---------------------------
# 🌐 Get related articles via Gemini
# ---------------------------
def get_articles_from_gemini(summary):
    prompt = f"""
    Based on this video summary, find 3 relevant and recent news article URLs that either support or refute 
    the main points made in the video. Return ONLY the URLs, one per line:
    
    {summary}
    """
    try:
        response = gemini_model.generate_content(prompt)
        # Clean the response to extract just URLs
        urls = [line.strip() for line in response.text.splitlines() 
               if line.strip().startswith(('http://', 'https://'))]
        return urls[:3]  # Return first 3 valid URLs
    except Exception as e:
        return [f"⚠ Error fetching URLs: {str(e)}"]

# ---------------------------
# 🔄 Compare summary with articles
# ---------------------------
def compare_with_articles(summary, article_urls):
    results = []
    
    for url in article_urls:
        try:
            # Skip if URL is an error message
            if url.startswith("⚠"):
                results.append({
                    'url': url,
                    'error': url
                })
                continue
                
            # Get article content
            article_content = get_article_content(url)
            
            # Skip if we got an error fetching content
            if article_content.startswith("⚠"):
                results.append({
                    'url': url,
                    'error': article_content
                })
                continue
                
            # Calculate similarity between summary and article
            summary_embedding = sentence_model.encode(summary, convert_to_tensor=True)
            article_embedding = sentence_model.encode(article_content, convert_to_tensor=True)
            
            similarity = util.pytorch_cos_sim(summary_embedding, article_embedding).item()
            
            # Determine verdict
            if similarity > 0.5:
                verdict = "Supports"
                verdict_color = "green"
            elif similarity < 0.3:
                verdict = "Contradicts"
                verdict_color = "red"
            else:
                verdict = "Neutral"
                verdict_color = "orange"
            
            results.append({
                'url': url,
                'content': article_content[:200] + "...",  # Preview of content
                'similarity': similarity,
                'verdict': verdict,
                'verdict_color': verdict_color
            })
        except Exception as e:
            results.append({
                'url': url,
                'error': f"⚠ Processing error: {str(e)}"
            })
    
    return results

# ---------------------------
# 🌐 Web UI
# ---------------------------
@app.route("/", methods=["GET", "POST"])
def home():
    analysis_results = []
    transcript = ""
    summary = ""
    video_url = ""

    if request.method == "POST":
        video_url = request.form.get("video_url")
        video_id = extract_video_id(video_url)

        if not video_id:
            return "❌ Invalid YouTube URL"

        # Step 1: Get transcript
        transcript = get_transcript(video_id)
        if transcript.startswith("⚠ Error"):
            return render_template_string("""
                <h2>Error</h2>
                <p>{{ error }}</p>
                <a href="/">Try again</a>
            """, error=transcript)

        # Step 2: Generate summary
        summary = generate_summary(transcript)
        if summary.startswith("⚠ Error"):
            return render_template_string("""
                <h2>Error</h2>
                <p>{{ error }}</p>
                <a href="/">Try again</a>
            """, error=summary)

        # Step 3: Get related articles
        article_urls = get_articles_from_gemini(summary)
        if not article_urls or article_urls[0].startswith("⚠"):
            return render_template_string("""
                <h2>Error</h2>
                <p>Failed to find related articles: {{ error }}</p>
                <a href="/">Try again</a>
            """, error=article_urls[0] if article_urls else "No articles found")

        # Step 4: Compare with articles
        analysis_results = compare_with_articles(summary, article_urls)

    return render_template_string("""
        <html>
        <head>
            <title>Video Fact Checker</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; }
                .summary { background: #f5f5f5; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
                table { width: 100%; border-collapse: collapse; margin-top: 20px; }
                th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
                th { background-color: #f2f2f2; }
                .content-preview { color: #666; font-size: 0.9em; }
                .error { color: red; }
            </style>
        </head>
        <body>
            <h1>🎥 YouTube Video Fact Checker</h1>
            <form method="POST">
                <input name="video_url" type="text" style="width: 70%; padding: 8px;" 
                       placeholder="Enter YouTube URL" value="{{ video_url }}" required>
                <button type="submit" style="padding: 8px 15px;">Analyze</button>
            </form>

            {% if summary %}
                <div class="summary">
                    <h3>📝 Video Summary</h3>
                    <p>{{ summary }}</p>
                </div>
            {% endif %}

            {% if analysis_results %}
                <h3>🔍 Verification Results</h3>
                <table>
                    <thead>
                        <tr>
                            <th>Article</th>
                            <th>Similarity</th>
                            <th>Verdict</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for result in analysis_results %}
                            <tr>
                                <td>
                                    <a href="{{ result.url }}" target="_blank">{{ result.url }}</a>
                                    {% if 'content' in result %}
                                        <div class="content-preview">{{ result.content }}</div>
                                    {% endif %}
                                    {% if 'error' in result %}
                                        <div class="error">{{ result.error }}</div>
                                    {% endif %}
                                </td>
                                {% if 'error' not in result %}
                                    <td>{{ "%.2f"|format(result.similarity) }}</td>
                                    <td style="color: {{ result.verdict_color }}">{{ result.verdict }}</td>
                                {% else %}
                                    <td colspan="2"></td>
                                {% endif %}
                            </tr>
                        {% endfor %}
                    </tbody>
                </table>
                
                <div style="margin-top: 20px; font-size: 0.9em; color: #666;">
                    <p><strong>How to interpret similarity scores:</strong></p>
                    <ul>
                        <li>1.0 = Perfect match</li>
                        <li>0.5-1.0 = Generally supports</li>
                        <li>0.3-0.5 = Neutral/Unrelated</li>
                        <li>0.0-0.3 = Generally contradicts</li>
                    </ul>
                </div>
            {% endif %}
        </body>
        </html>
    """, analysis_results=analysis_results, transcript=transcript, summary=summary, video_url=video_url)

# ---------------------------
# ▶ Run the app
# ---------------------------
if __name__ == "__main__":
    app.run(debug=True)