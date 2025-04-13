from flask import Flask, request, jsonify
import google.generativeai as genai
import re
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Configure Gemini API Key
genai.configure(api_key="nice try")
KeywordModel = genai.GenerativeModel("gemini-1.5-pro-latest")

@app.route('/articlekeyword', methods=['POST'])
def article_keyword():
    data = request.get_json()
    user_input = data.get("news_input")

    if not user_input:
        return jsonify({"error": "Missing 'news_input' field"}), 400

    prompt = f"""
    I have a statement: "{user_input}"

    Please tell me:
    1. Is it Verified, Unverified, or Partially Verified?
    2. Give a credibility score out of 100.

    Format your response exactly like this (no extra words):
    Verification: <status>
    Credibility Score: <score>/100
    """

    try:
        response = KeywordModel.generate_content(prompt)
        raw_output = response.text
        print("Gemini Response:\n", raw_output)  # Debug log

        # Use regex to extract data
        verification_match = re.search(r"Verification:\s*(.*)", raw_output, re.IGNORECASE)
        score_match = re.search(r"Credibility Score:\s*(\d+)", raw_output, re.IGNORECASE)

        verification = verification_match.group(1).strip() if verification_match else "Not Available"
        credibility_score = score_match.group(1).strip() if score_match else "0"

        return jsonify({
            "verification": verification,
            "credibility_score": credibility_score
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
