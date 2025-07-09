import os
import openai
import google.generativeai as genai
from google.cloud import texttospeech
from transformers import pipeline

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