import os
import re
import keras_ocr
import google.generativeai as genai
from transformers import pipeline
from flask import Flask, request, jsonify
from flask_cors import CORS

# ✅ Initialize Flask App
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# ✅ Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))  # Replace with your actual API key

# ✅ OCR Function using keras-ocr
def ocr_with_keras(image_path):
    pipeline = keras_ocr.pipeline.Pipeline()
    image = keras_ocr.tools.read(image_path)
    predictions = pipeline.recognize([image])
    extracted_text = " ".join([text for text, _ in predictions[0]])
    return extracted_text

# ✅ Summarization Function
def summarize_text(text, max_length=150, min_length=50):
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    max_chunk_size = 1024
    chunks = [text[i:i + max_chunk_size] for i in range(0, len(text), max_chunk_size)]
    summaries = [summarizer(chunk, max_length=max_length, min_length=min_length, do_sample=False)[0]['summary_text'] for chunk in chunks]
    return ' '.join(summaries)

# ✅ Extract Key Points
def extract_key_points(summary):
    sentences = re.split(r'[.!?]+', summary)
    key_points = [s.strip() for s in sentences if len(s.strip()) > 20]
    return key_points

# ✅ Verify News with Gemini
def verify_news_with_gemini(summary):
    try:
        model = genai.GenerativeModel("gemini-1.5-pro-latest")
        prompt = f"""
        Verify the authenticity of the following text extracted from an image.  
        - Provide a **truthfulness rating** (True, Partially True, False).  
        - List **at least two sources with URLs** that confirm or contradict this news.  
        - Assign a **credibility score (1-10)** to each source based on reliability.  
        - Summarize key findings from these sources.  

        **Extracted Text Summary:** {summary}
        """
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"⚠️ Error in verification: {str(e)}"

# ✅ API Route for OCR Analysis
@app.route("/OCR", methods=["POST"])
def OCR():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400
    
    image_file = request.files["image"]
    if image_file.filename == "":
        return jsonify({"error": "No selected image"}), 400
    
    # Save the uploaded image temporarily
    image_path = "temp_uploaded_image.jpg"
    image_file.save(image_path)
    
    try:
        # ✅ Extract text from image
        extracted_text = ocr_with_keras(image_path)
        
        # ✅ Summarize extracted text (if long)
        summary = summarize_text(extracted_text) if len(extracted_text) > 300 else extracted_text
        
        # ✅ Extract key points
        key_points = extract_key_points(summary)
        
        # ✅ Verify news authenticity using Gemini API
        verification_result = verify_news_with_gemini(summary)
        
        return jsonify({
            "extracted_text": extracted_text,
            "summary": summary,
            "key_points": key_points,
            "verification_result": verification_result
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    finally:
        # Remove the temporary image file
        if os.path.exists(image_path):
            os.remove(image_path)

# ✅ Run Flask App
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5001)
