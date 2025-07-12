# frontend/app.py
import streamlit as st
import requests
import uuid
from audiorecorder import audiorecorder
import os

# --- Page Configuration ---
st.set_page_config(
    page_title="Elile | إليل",
    page_icon="🇴🇲"
)

# --- Session State Initialization ---
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.chat_history = []
    # --- NEW: Key for resetting the audio recorder ---
    st.session_state.recorder_key = "recorder_0"

# --- Backend API URL ---
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000/chat")

# --- UI Components ---
st.title("إليل | Elile")
st.markdown("رفيقك الصوتي للصحة النفسية في عُمان")
st.markdown("---")

# Display chat history
if st.session_state.chat_history:
    for user_msg, ai_audio, media_type in st.session_state.chat_history:
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
        st.audio(ai_audio, format=media_type)

st.markdown("---")

# Audio recorder button at the bottom
st.write("اضغط للتحدث مع إليل")
# --- MODIFIED: Pass the unique key to the component ---
audio = audiorecorder("▶️ تسجيل", "⏹️ إيقاف", key=st.session_state.recorder_key)


# --- NEW, SIMPLIFIED LOGIC ---
if len(audio) > 0:
    # Get the audio recording bytes
    audio_bytes = audio.export().read()

    with st.spinner("إليل يستمع ويفكر..."):
        try:
            # Prepare data for the API request
            files = {'audio_file': ('recording.wav', audio_bytes, 'audio/wav')}
            data = {'session_id': st.session_state.session_id}

            # Send request to backend
            response = requests.post(BACKEND_URL, files=files, data=data)

            if response.status_code == 200:
                media_type = response.headers.get('Content-Type', 'audio/wav')
                user_transcribed_text = "(قمت بتسجيل رسالة صوتية)"
                ai_audio_response = response.content

                # Update chat history
                st.session_state.chat_history.append(
                    (user_transcribed_text, ai_audio_response, media_type)
                )

                # --- THE DEFINITIVE FIX ---
                # Increment the key to force a full re-initialization of the recorder
                current_key_index = int(st.session_state.recorder_key.split('_')[1])
                st.session_state.recorder_key = f"recorder_{current_key_index + 1}"
                
                # Rerun to display the new message and the new, empty recorder
                st.rerun()

            else:
                st.error(f"حدث خطأ. حاول مرة أخرى. (Error: {response.status_code})")
                st.error(f"Details: {response.text}")

        except requests.exceptions.RequestException as e:
            st.error(f"لا يمكن الاتصال بالخادم. تأكد من أنه يعمل. (Connection Error: {e})")