import os
import uuid
import time
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
import services
import database
import io

# Load environment variables and initialize database
load_dotenv()
database.init_db()

app = FastAPI()

@app.post("/chat")
async def chat_endpoint(session_id: str, audio_file: UploadFile = File(...)):
    start_time = time.time()

    # 1. Save audio file temporarily
    temp_audio_path = f"/tmp/{uuid.uuid4()}.wav"
    with open(temp_audio_path, "wb") as f:
        f.write(await audio_file.read())

    try:
        # 2. Voice Capture & STT
        user_text = services.transcribe_audio(temp_audio_path)
        if not user_text:
            raise HTTPException(status_code=400, detail="Could not understand audio.")
        
        # 3. Intent Analysis (Emotion)
        emotion = services.detect_emotion(user_text)

        # Retrieve conversation history
        history = database.get_conversation_history(session_id)

        # 4. Dual-Model Response Generation & 5. Cultural Adaptation (handled by prompt)
        ai_text_response = services.generate_response(history, user_text, emotion)

        # Log the full conversation turn to the database
        database.log_conversation(session_id, user_text, emotion, ai_text_response)

        # 6. TTS Output
        ai_audio_response = services.synthesize_speech(ai_text_response)

        end_time = time.time()
        latency = end_time - start_time
        print(f"Processed turn in {latency:.2f} seconds.")

        # Check against performance constraint
        if latency > 20:
            print("Warning: End-to-end latency exceeded 20 seconds.")

        # 7. Return audio response
        return StreamingResponse(io.BytesIO(ai_audio_response), media_type="audio/mpeg")

    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Clean up the temporary audio file
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)

@app.get("/")
def read_root():
    return {"status": "OMANI-Therapist-Voice Backend is running."}