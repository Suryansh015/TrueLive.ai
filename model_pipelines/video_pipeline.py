import os
import subprocess
from vosk import Model, KaldiRecognizer
import wave
import json
from transformers import AutoModelForSequenceClassification, AutoTokenizer

# Extract and Resample Audio from Video
def extract_and_resample_audio(video_path, output_audio_path="temp_audio.wav", target_sample_rate=16000):
    try:
        print(f"Extracting and resampling audio from {video_path} to {output_audio_path}...")
        result = subprocess.run(
            ["ffmpeg", "-y", "-i", video_path, "-ar", str(target_sample_rate), "-ac", "1", "-sample_fmt", "s16", output_audio_path],
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True
        )
        if result.returncode != 0:
            print(f"FFmpeg error:\n{result.stderr}")
            return None
        print(f"Audio extracted and resampled to {target_sample_rate} Hz: {output_audio_path}")
        return output_audio_path
    except Exception as e:
        print(f"Error extracting and resampling audio: {e}")
        return None

#  Vosk asr
vosk_model_path = r"path_to_your_vosk_asr_model" 
if not os.path.exists(vosk_model_path):
    raise FileNotFoundError(f"Vosk model not found at {vosk_model_path}. Please download it.")

vosk_model = Model(vosk_model_path)

# Step 3: Transcribe Audio Using Vosk
def transcribe_audio_vosk(audio_path):
    try:
        with wave.open(audio_path, "rb") as wf:
            if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() != 16000:
                raise ValueError("Audio file must be WAV format with 1 channel, 16-bit samples, and 16 kHz sample rate.")

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
        print(f"Error transcribing audio: {e}")
        return ""

MODEL_PATH = r"path_to_your_ba-claim/distilbert"
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)

# Check Claims
def check_claim(claim):
    try:
        # perform inference
        inputs = tokenizer(claim, return_tensors="pt", truncation=True, padding=True, max_length=512)
        outputs = model(**inputs)
        logits = outputs.logits
        predicted_class_id = logits.argmax().item()
        confidence_score = logits.softmax(dim=1).max().item()  # Get the confidence scor

        
        if predicted_class_id == 1:  
            return f"The claim is TRUE with a confidence score of {confidence_score:.2f}."
        else:  
            return f"The claim might be FALSE or UNVERIFIED with a confidence score of {confidence_score:.2f}."
    except Exception as e:
        print(f"Error checking claim: {e}")
        return "Error in claim verification."

#Pipeline for Fact-Checking Local Video
def fact_check_local_video(video_path):
    print("Starting fact-checking process...")

    # Extract and resample audio
    audio_path = extract_and_resample_audio(video_path)
    if not audio_path:
        print("Audio extraction failed. Exiting.")
        return

    # Transcribe the audio
    transcription = transcribe_audio_vosk(audio_path)
    if not transcription:
        print("Failed to transcribe audio. Exiting.")
        return

    # transcription to a file
    with open("transcription_output.txt", "w", encoding="utf-8") as file:
        file.write(transcription)

    # UTF-8 encoding
    try:
        print(f"Transcription:\n{transcription.encode('utf-8').decode('utf-8')}\n")
    except Exception as e:
        print(f"Error displaying transcription: {e}")
        print(f"Raw transcription saved to transcription_output.txt")
    claim_result = check_claim(transcription)
    print(f"Claim Verification Result:\n{claim_result}\n")

video_path = r"C:\Users\Dell\Downloads\videoplayback (1).mp4" 
fact_check_local_video(video_path)
