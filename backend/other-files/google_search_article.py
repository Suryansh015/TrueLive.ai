import os
import time
import torch
import logging
from newspaper import Article
from flask import Flask, request, render_template_string
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from googleapiclient.discovery import build
from sentence_transformers import SentenceTransformer, util
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup

# 🚀 Google API Credentials
GOOGLE_API_KEY = "nice try"
GOOGLE_CSE_ID = "nice try"
# ❌ List of Known Fake/Unreliable News Sources
FAKE_SOURCES = {
    "beforeitsnews.com", "worldtruth.tv", "naturalnews.com",
    "infowars.com", "breitbart.com", "yournewswire.com",
    "newsbreak.com", "theblaze.com", "conservativetreehouse.com",
    "wnd.com", "thegatewaypundit.com", "thedailybeast.com",
    "newsthump.com", "breakingnewsandreligion.online", 
    "theonion.com"
}

# 🔍 Social Media Platforms to Check for External Links
SOCIAL_MEDIA_SITES = {"tumblr.com", "reddit.com", "twitter.com", "facebook.com", "tiktok.com"}

# 🌍 Initialize Flask App
app = Flask(__name__)

# 📌 Load Local Claim Extraction Model
MODEL_PATH = r"C:\Users\surya\Desktop\Programs\web-projects\truelive.ai\AI models\old models (big ahh)\_token model 1"
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)

# 📌 Load Similarity Model for Verification
similarity_model = SentenceTransformer("all-MiniLM-L6-v2")

# 📰 Extract Domain from URL
def extract_domain(url):
    try:
        parsed_url = urlparse(url)
        return parsed_url.netloc.replace("www.", "")
    except Exception:
        return None

# 📰 Extract External Links from Social Media
def extract_external_links(social_media_url):
    """Scrapes a social media page to find any external links mentioned in the post."""
    try:
        response = requests.get(social_media_url, timeout=5)
        soup = BeautifulSoup(response.text, "html.parser")
        links = [a["href"] for a in soup.find_all("a", href=True)]
        return links
    except Exception:
        return []

# 📰 Extract Claims
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

# 🔍 Verify Claim with Search
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
                logging.info(f"🔍 Social media post detected: {source_url}")
                external_links = extract_external_links(source_url)

                # Search for a reliable external link within the social media post
                reliable_link_found = False
                for sub_link in external_links:
                    sub_domain = extract_domain(sub_link)
                    if sub_domain not in FAKE_SOURCES and sub_domain != input_domain:
                        logging.info(f"✅ Found reliable external link: {sub_link}")
                        source_url = sub_link
                        source_domain = sub_domain
                        reliable_link_found = True
                        break

                if not reliable_link_found:
                    logging.info(f"❌ No reliable sources in social media post: {source_url}")
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

# 🌐 HTML Template for Rendering
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>News Verification</title>
</head>
<body>
<h2>News Verification System</h2>
<form method="post">
    <input type="text" name="url" placeholder="Enter News Article URL" required>
    <button type="submit">Verify News</button>
</form>

{% if claims %}
<div>
    <h3>Extracted Claims:</h3>
    {% for claim, confidence in claims %}
        <p>Claim: "{{ claim }}" (Confidence: {{ confidence|round(2) }})</p>
    {% endfor %}

    <h3>Verification Results:</h3>
    <p><strong>Best Source:</strong> <a href="{{ best_source }}">{{ best_source }}</a></p>
    <p><strong>Confidence Score:</strong> {{ best_confidence|round(2) }}</p>
    <p><strong>Verdict:</strong> {% if is_true %} ✅ Likely True {% else %} ❌ Likely False {% endif %}</p>
</div>
{% endif %}
</body>
</html>
"""

# 🏁 Flask Routes
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        article_url = request.form["url"]
        try:
            article = Article(article_url)
            article.download()
            article.parse()
            title = article.title
            text = article.text

            claims = extract_claims(text, title)
            if not claims:
                return render_template_string(HTML_TEMPLATE, error="No claims extracted.")

            best_claim = claims[0][0]
            best_source, best_confidence, is_true = verify_claim_with_search(best_claim, article_url)

            return render_template_string(HTML_TEMPLATE, claims=claims, best_source=best_source, best_confidence=best_confidence, is_true=is_true)

        except Exception as e:
            return render_template_string(HTML_TEMPLATE, error=str(e))

    return render_template_string(HTML_TEMPLATE)

# 🚀 Run Flask App
if __name__ == '__main__':
    app.run(debug=True)
