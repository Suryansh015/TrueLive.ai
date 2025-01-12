import os
import subprocess
from flask import Flask, request, render_template_string, jsonify
from vosk import Model, KaldiRecognizer
import wave
import json
from transformers import AutoModelForSequenceClassification, AutoTokenizer

app = Flask(__name__)

VOSK_MODEL_PATH = r"path_to_your_vosk-model-en-in-0.5"
TRANSFORMER_MODEL_PATH = r"path_to_your_ba-claim/distilbert"

vosk_model = Model(VOSK_MODEL_PATH)
tokenizer = AutoTokenizer.from_pretrained(TRANSFORMER_MODEL_PATH)
model = AutoModelForSequenceClassification.from_pretrained(TRANSFORMER_MODEL_PATH)

#  extract and resample audio from video
def extract_and_resample_audio(video_path, output_audio_path="temp_audio.wav", target_sample_rate=16000):
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-i", video_path, "-ar", str(target_sample_rate), "-ac", "1", "-sample_fmt", "s16", output_audio_path],
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True
        )
        return output_audio_path
    except Exception as e:
        return None

# transcribe audio using Vosk
def transcribe_audio_vosk(audio_path):
    try:
        with wave.open(audio_path, "rb") as wf:
            recognizer = KaldiRecognizer(vosk_model, wf.getframerate())
            recognizer.SetWords(True)

            transcription = ""
            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    transcription += result.get("text", "") + " "

            final_result = json.loads(recognizer.FinalResult())
            transcription += final_result.get("text", "")
            return transcription.strip()
    except Exception as e:
        return ""

# verify claims using the transformer model
def check_claim(claim):
    try:
        inputs = tokenizer(claim, return_tensors="pt", truncation=True, padding=True, max_length=512)
        outputs = model(**inputs)
        logits = outputs.logits
        predicted_class_id = logits.argmax().item()
        confidence_score = logits.softmax(dim=1).max().item()

        if predicted_class_id == 1:
            return f"TRUE with confidence {confidence_score:.2f}"
        else:
            return f"FALSE/UNVERIFIED with confidence {confidence_score:.2f}"
    except Exception as e:
        return "Error in claim verification."

@app.route('/', methods=['GET', 'POST'])
def home():
    result = None
    transcription = None
    error_message = None

    if request.method == 'POST':
        try:

            if 'video' not in request.files:
                error_message = "No file uploaded."
                return render_template_string(html_template, result=result, transcription=transcription, error_message=error_message)

            video_file = request.files['video']
            video_path = "uploaded_video.mp4"
            video_file.save(video_path)

            #Extract and resample audio
            audio_path = extract_and_resample_audio(video_path)
            if not audio_path:
                error_message = "Audio extraction failed."
                return render_template_string(html_template, result=result, transcription=transcription, error_message=error_message)

            # Transcribe the audio
            transcription = transcribe_audio_vosk(audio_path)
            if not transcription:
                error_message = "Audio transcription failed."
                return render_template_string(html_template, result=result, transcription=transcription, error_message=error_message)

            #  Verify claims
            result = check_claim(transcription)

        except Exception as e:
            error_message = f"Error processing video: {str(e)}"

    # HTML template
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Fact-Checking API</title>
    </head>
    <body>
        <h1>Fact-Checking API</h1>
        <form method="POST" action="/" enctype="multipart/form-data">
            <label for="video">Upload a video file:</label><br>
            <input type="file" id="video" name="video" required><br><br>
            <button type="submit">Submit</button>
        </form>
        
        {% if error_message %}
        <p style="color: red;">{{ error_message }}</p>
        {% endif %}

        {% if transcription %}
        <h2>Transcription</h2>
        <p>{{ transcription }}</p>
        {% endif %}

        {% if result %}
        <h2>Claim Verification Result</h2>
        <p>{{ result }}</p>
        {% endif %}
    </body>
    </html>
    """
    return render_template_string(html_template, result=result, transcription=transcription, error_message=error_message)

if __name__ == '__main__':
    app.run(debug=True)
