# OMANI-Therapist-Voice

This project is a proof-of-concept for a voice-only, Omani Arabic mental health chatbot. It's built to provide culturally sensitive, therapeutic-grade conversations in real-time.

## Final Architecture

- **Backend**: FastAPI server that handles all AI processing.
- **Frontend**: Streamlit application for the real-time voice interface.
- **STT (Speech-to-Text)**: OpenAI Whisper API.
- **Emotion Detection**: Hugging Face `bhadresh-savani/bert-base-go-emotion` model (local).
- **Response Generation**: GPT-4o with a fallback to Google's Gemini Flash.
- **TTS (Text-to-Speech)**: Hugging Face `facebook/mms-tts-arb` model (local, free). This provides a high-quality Modern Standard Arabic voice.
- **Database**: SQLite for storing conversation history.
- **Hosting**: Pre-configured for deployment on Render.

## Key Features

- **Voice-Only Interaction**: The primary interface is through voice, creating a natural and accessible user experience.
- **Cultural Sensitivity**: The AI is prompted to understand and respect Omani and Gulf cultural norms, including family dynamics and Islamic values.
- **Dual-Model Strategy**: Uses GPT-4o for primary responses and falls back to Gemini Flash, ensuring high availability and reliability.
- **Local, Free TTS**: Avoids costly API fees by using a state-of-the-art, locally-run model for voice generation.
- **Real-time Latency Optimizations**: Implements a model "warm-up" on server start to reduce latency on initial user interactions.

## Setup and Running the Application

### 1. Prerequisites
- Python 3.9+
- A virtual environment tool (like `venv`)

### 2. Clone the Repository
```bash
git clone https://github.com/myself-nahid/OMANI-Therapist-Voice.git
cd OMANI-Therapist-Voice
```

### 3. Create and Activate Virtual Environment
```bash
# For macOS/Linux
python3 -m venv venv
source venv/bin/activate

# For Windows
python -m venv venv
.
env\Scripts ctivate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

Create a file named `.env` in the root directory and add the following:

```env
# .env

# Get from https://platform.openai.com/api-keys
OPENAI_API_KEY="YOUR_OPENAI_API_KEY"

# Get from https://aistudio.google.com/app/apikey
GOOGLE_AI_STUDIO_API_KEY="YOUR_GEMINI_API_KEY"
```

> 📝 **Note**: Google Cloud credentials are no longer needed as we are not using Google TTS.

### 6. Run the Application

You need to run the backend and frontend in two separate terminal windows.

**Terminal 1: Start the Backend Server**
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```
> 🔄 The first time you run this, it will download the Hugging Face models (Emotion Detection and TTS). The TTS model is over 2GB, so this may take a while. You will also see "warm-up" logs as the server prepares the models. This is a one-time process.

**Terminal 2: Start the Frontend Application**
```bash
streamlit run frontend/app.py
```

### 7. Access the Chatbot

Open your browser and go to: [http://localhost:8501](http://localhost:8501)  
Grant microphone access when prompted and start your conversation.

---
