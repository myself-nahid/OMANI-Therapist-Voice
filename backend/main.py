# backend/main.py
import os
import uuid
import time
import tempfile  # For cross-platform temporary file handling
import io
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from backend import services
from backend import database

# Load environment variables from .env file and initialize the database
load_dotenv()
database.init_db()

# Initialize the FastAPI app
app = FastAPI()

@app.post("/chat")
async def chat_endpoint(session_id: str = Form(...), audio_file: UploadFile = File(...)):
    """
    This endpoint handles the entire voice conversation pipeline.
    It receives an audio file and a session ID, processes them, and returns an audio response.
    """
    start_time = time.time()
    temp_audio_path = None  # Initialize path variable to ensure it's available in 'finally'

    try:
        # Create a temporary file to store the uploaded audio in a cross-platform way.
        # 'delete=False' allows us to get the file path before it's automatically deleted.
        # We will manually delete it in the 'finally' block.
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            temp_file.write(await audio_file.read())
            temp_audio_path = temp_file.name

        # --- Speech Processing Pipeline ---

        # 1. Voice Capture & STT: Transcribe the audio file to text.
        user_text = services.transcribe_audio(temp_audio_path)
        if not user_text.strip():
            raise HTTPException(status_code=400, detail="Could not understand audio or the speech was empty.")

        # 2. Intent Analysis: Detect the user's emotion from the text.
        emotion = services.detect_emotion(user_text)

        # Retrieve the recent conversation history for context.
        history = database.get_conversation_history(session_id)

        # 3. Dual-Model Response Generation & 4. Cultural Adaptation (handled by prompt).
        ai_text_response = services.generate_response(history, user_text, emotion)

        # Log the complete interaction to the database for future context.
        database.log_conversation(session_id, user_text, emotion, ai_text_response)

        # 5. TTS Output: Convert the AI's text response into speech.
        ai_audio_response = services.synthesize_speech(ai_text_response)

        # --- Performance & Response ---
        end_time = time.time()
        latency = end_time - start_time
        print(f"Processed turn for session '{session_id}' in {latency:.2f} seconds.")

        # Check against the performance constraint.
        if latency > 20:
            print(f"WARNING: End-to-end latency ({latency:.2f}s) exceeded the 20-second target.")

        # 6. Stream the generated audio back to the client.
        return StreamingResponse(io.BytesIO(ai_audio_response), media_type="audio/wav")

    except Exception as e:
        print(f"An error occurred during the chat process: {e}")
        # Return a generic server error to the client.
        raise HTTPException(status_code=500, detail="An internal server error occurred.")
        
    finally:
        # Clean up: always remove the temporary audio file if it was created.
        if temp_audio_path and os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)


@app.get("/")
def read_root():
    """
    A simple root endpoint to check if the backend server is running.
    """
    return {"status": "OMANI-Therapist-Voice Backend is running."}