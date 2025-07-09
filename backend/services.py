# backend/services.py
import os
import openai
import google.generativeai as genai
from google.cloud import texttospeech
from transformers import pipeline
from prompts import get_system_prompt

# --- Initialize Clients and Models (Load only once) ---
# OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Google Gemini
genai.configure(api_key=os.getenv("GOOGLE_AI_STUDIO_API_KEY"))
gemini_model = genai.GenerativeModel('gemini-1.5-flash')

# Google TTS
tts_client = texttospeech.TextToSpeechClient()

# Hugging Face Emotion Detection
emotion_classifier = pipeline("text-classification", model="bhadresh-savani/bert-base-go-emotion", top_k=1)

# --- Service Functions ---

def transcribe_audio(audio_file_path: str) -> str:
    """Transcribes audio using OpenAI Whisper API."""
    try:
        with open(audio_file_path, "rb") as audio_file:
            # Using Omani Arabic ('ar') as the language hint
            transcription = openai.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="ar",
                prompt="هذه محادثة باللهجة العمانية." # Prompt to hint at the dialect
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
    
    # Construct the message list for the API call
    messages = [
        {"role": "system", "content": system_prompt},
    ]
    messages.extend(history)
    messages.append({"role": "user", "content": f"(Detected Emotion: {emotion}) {user_text}"})

    # Primary Model: GPT-4o
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
        
        # Fallback Model: Gemini 1.5 Flash
        try:
            # Gemini has a different message format
            gemini_history = [m for m in messages if m['role'] != 'system']
            full_prompt = f"{system_prompt}\n\n---\n\nConversation History:\n{gemini_history}\n\n---\n\nUser said: {user_text}\n(Detected Emotion: {emotion})"
            
            response = gemini_model.generate_content(full_prompt)
            return response.text.strip()
        except Exception as e_gemini:
            print(f"Gemini fallback also failed: {e_gemini}")
            return "عذراً، أواجه مشكلة فنية في الوقت الحالي. هل يمكنك إعادة ما قلته؟" # Sorry, I'm having a technical issue...

def synthesize_speech(text: str) -> bytes:
    """Synthesizes text to speech using Google Cloud TTS."""
    synthesis_input = texttospeech.SynthesisInput(text=text)
    
    # Select a high-quality Arabic voice.
    # ar-XA-Wavenet-B is a good, calm female voice. Test for Omani accent suitability.
    voice = texttospeech.VoiceSelectionParams(
        language_code="ar-XA",
        name="ar-XA-Wavenet-B",
        ssml_gender=texttospeech.SsmlVoiceGender.FEMALE,
    )
    
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )
    
    response = tts_client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )
    
    return response.audio_content