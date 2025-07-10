# frontend/app.py
import streamlit as st
import requests
import uuid
from audiorecorder import audiorecorder
import os # Good practice to import os if using it

# --- Page Configuration ---
st.set_page_config(
    page_title="Elile | إليل",
    page_icon="🇴🇲"
)

# --- Session State Initialization ---
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
    
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# --- Backend API URL ---
# Use an environment variable for deployment flexibility, with a local fallback
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000/chat")

# --- UI Components ---
st.title("إليل | Elile")
st.markdown("رفيقك الصوتي للصحة النفسية في عُمان")
st.markdown("---")

# Display chat history
if st.session_state.chat_history:
    for i, (user_msg, ai_audio, media_type) in enumerate(st.session_state.chat_history):
        # Display user message
        message_alignment = "flex-end"
        message_bg_color = "linear-gradient(135deg, #00B2A9 0%, #00827B 100%)"
        st.markdown(f"""
        <div style="display: flex; justify-content: {message_alignment}; margin-bottom: 10px;">
            <div style="background: {message_bg_color}; color: white; border-radius: 20px; padding: 10px 15px; max-width: 70%;">
                <b>أنت:</b> {user_msg}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Display AI response
        st.write("**إليل:**")
        st.audio(ai_audio, format=media_type) # Use the stored media type

st.markdown("---")

# Audio recorder button at the bottom
st.write("اضغط للتحدث مع إليل")
audio = audiorecorder("▶️ تسجيل", "⏹️ إيقاف")

if len(audio) > 0:
    audio_bytes = audio.export().read()

    with st.spinner("إليل يستمع ويفكر..."):
        try:
            # --- THIS IS THE BLOCK TO CHANGE ---
            
            # 1. Prepare the files payload
            files = {'audio_file': ('recording.wav', audio_bytes, 'audio/wav')}
            
            # 2. Prepare the data payload (for form fields)
            data = {'session_id': st.session_state.session_id}

            # 3. Send the request with BOTH files and data.
            #    Remove the 'params' argument.
            response = requests.post(BACKEND_URL, files=files, data=data)
            
            # --- END OF CHANGE BLOCK ---

            if response.status_code == 200:
                # Get the media type from the response headers
                media_type = response.headers.get('Content-Type', 'audio/wav')
                
                # A better implementation would have the backend return a JSON object
                # with both the transcribed text and the audio response.
                # For now, let's just use a placeholder for the user's message.
                user_transcribed_text = "(قمت بتسجيل رسالة صوتية)"
                ai_audio_response = response.content

                # Update chat history including the media type
                st.session_state.chat_history.append(
                    (user_transcribed_text, ai_audio_response, media_type)
                )
                
                st.rerun()

            else:
                st.error(f"حدث خطأ. حاول مرة أخرى. (Error: {response.status_code})")
                st.error(f"Details: {response.text}")

        except requests.exceptions.RequestException as e:
            st.error(f"لا يمكن الاتصال بالخادم. تأكد من أنه يعمل. (Connection Error: {e})")