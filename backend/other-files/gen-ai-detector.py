from flask import Flask, request, jsonify
from transformers import pipeline
from PIL import Image
import torch
import io
from flask_cors import CORS

# Initialize Flask app
app = Flask(__name__) 
CORS(app, resources={r"/*": {"origins": "*"}})

# Load Hugging Face model
device = "cuda" if torch.cuda.is_available() else "cpu"
classifier = pipeline("image-classification", model="umm-maybe/AI-image-detector", device=0 if device == "cuda" else -1)

@app.route("/genAI", methods=["POST"])
def genAI_Det():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    try:
        # Convert image to PIL format
        image = Image.open(io.BytesIO(file.read())).convert("RGB")

        # Run the model prediction
        result = classifier(image)[0]
        prediction = result["label"]
        confidence = result["score"] * 100  # Convert to percentage

        return jsonify({
            "status": "success",
            "prediction": prediction,
            "confidence": confidence
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
