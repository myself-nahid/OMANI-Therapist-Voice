# backend/services.py
import os
import io
import openai
import google.generativeai as genai
from transformers import pipeline
from backend.prompts import get_system_prompt
import torch
import soundfile as sf

# --- NEW: Import MMS model components from transformers ---
from transformers import VitsModel, AutoTokenizer

# --- Initialize Clients and Models (Load only once) ---
# OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Google Gemini
genai.configure(api_key=os.getenv("GOOGLE_AI_STUDIO_API_KEY"))
gemini_model = genai.GenerativeModel('gemini-1.5-flash')

# Hugging Face Emotion Detection
emotion_classifier = pipeline("text-classification", model="bhadresh-savani/bert-base-go-emotion", top_k=1)


# --- NEW: Load the MMS Text-to-Speech model and tokenizer ---
print("Loading MMS TTS model for Arabic...")
# This will download the model (around 2GB) the first time you run it.
tts_model = VitsModel.from_pretrained("facebook/mms-tts-ara")
tts_tokenizer = AutoTokenizer.from_pretrained("facebook/mms-tts-ara")
print("MMS TTS model loaded successfully.")

# --- Service Functions ---

def transcribe_audio(audio_file_path: str) -> str:
    """Transcribes audio using OpenAI Whisper API."""
    try:
        with open(audio_file_path, "rb") as audio_file:
            transcription = openai.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="ar",
                prompt="هذه محادثة باللهجة العمانية."
            )
        return transcription.text
    except Exception as e:
        print(f"Error in transcription: {e}")
        return ""

def detect_emotion(text: str) -> str:
    """Detects emotion from text using a Hugging Face model."""
    if not text:
        return "neutral"
    try:
        results = emotion_classifier(text)
        return results[0][0]['label']
    except Exception as e:
        print(f"Error in emotion detection: {e}")
        return "neutral"

def generate_response(history: list, user_text: str, emotion: str) -> str:
    """Generates a response using GPT-4o with Gemini as a fallback."""
    system_prompt = get_system_prompt()
    
    messages = [
        {"role": "system", "content": system_prompt},
    ]
    messages.extend(history)
    messages.append({"role": "user", "content": f"(Detected Emotion: {emotion}) {user_text}"})

    try:
        print("Attempting to generate response with GPT-4o...")
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.7,
            max_tokens=200
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"GPT-4o failed: {e}. Falling back to Gemini Flash.")
        try:
            gemini_history = [m for m in messages if m['role'] != 'system']
            full_prompt = f"{system_prompt}\n\n---\n\nConversation History:\n{gemini_history}\n\n---\n\nUser said: {user_text}\n(Detected Emotion: {emotion})"
            
            response = gemini_model.generate_content(full_prompt)
            return response.text.strip()
        except Exception as e_gemini:
            print(f"Gemini fallback also failed: {e_gemini}")
            return "عذراً، أواجه مشكلة فنية في الوقت الحالي. هل يمكنك إعادة ما قلته؟"

# --- REPLACED: The synthesize_speech function ---
def synthesize_speech(text: str) -> bytes:
    """
    Synthesizes text to speech using the local Facebook MMS model.
    The output format is WAV, which we will convert to MP3/MPEG for streaming.
    """
    print(f"Synthesizing speech for text: {text}")
    inputs = tts_tokenizer(text, return_tensors="pt")

    with torch.no_grad():
        output = tts_model(**inputs).waveform

    # The output is a raw waveform. We need to save it as a proper audio file in memory.
    # The MMS model's sampling rate is 16000 Hz.
    sampling_rate = 16000
    
    # Use an in-memory buffer (BytesIO) to hold the WAV file data.
    buffer = io.BytesIO()
    sf.write(buffer, output.cpu().numpy().squeeze(), sampling_rate, format='WAV')
    
    # Reset buffer's position to the beginning to be read.
    buffer.seek(0)
    
    # Return the raw bytes of the WAV file.
    # Most browsers can play WAV, but we can also convert to MP3 if needed.
    # For now, let's keep it simple. We will tell the frontend it's 'audio/wav'.
    return buffer.read()

# --- NEW: WARM-UP FUNCTION ---
def warmup_models():
    """
    Warms up the AI models to reduce latency on the first user request.
    """
    print("Warming up models...")
    # 1. Warm up Emotion Detection
    try:
        detect_emotion("This is a test to warm up the emotion detection model.")
        print("Emotion detection model is warm.")
    except Exception as e:
        print(f"Could not warm up emotion model: {e}")

    # 2. Warm up TTS model
    try:
        # Synthesize a short, silent, or simple phrase.
        # This forces the model to load all necessary components and caches.
        print("Warming up TTS model... (This may take a moment)")
        synthesize_speech("أهلاً")
        print("TTS model is warm.")
    except Exception as e:
        print(f"Could not warm up TTS model: {e}")
    
    print("--- Models are warm and ready ---")

# --- Run the warm-up process when the service starts ---
warmup_models()