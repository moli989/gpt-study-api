import streamlit as st
import requests
import tempfile
import base64

st.title("🎙️ GPT Study Assistant with Voice")

if "history" not in st.session_state:
    st.session_state.history = []

user_id = st.text_input("Participant ID:")

# === Voice Input ===
st.markdown("#### 🎤 Speak your question (or type below)")
audio_file = st.file_uploader("Upload your voice (MP3/WAV/M4A)", type=["mp3", "wav", "m4a"])

if audio_file:
    # Send to Whisper
    res = requests.post("http://localhost:5000/whisper", files={"audio": audio_file})
    text = res.json()["text"]
    st.write(f"📝 Transcribed Text: {text}")
    st.session_state["latest_input"] = text
else:
    st.session_state["latest_input"] = st.text_input("Or type your message:")

# === Send message ===
if st.button("Send") and st.session_state["latest_input"]:
    payload = {
        "user_id": user_id,
        "message": st.session_state["latest_input"],
        "history": st.session_state.history
    }

    try:
        res = requests.post("http://localhost:5000/chat", json=payload)
        data = res.json()
        reply = data["reply"]
        st.session_state.history = data["new_history"]

        st.text_area("Assistant says:", reply, height=150)

        # === TTS: Get and play audio ===
        tts_res = requests.post("http://localhost:5000/tts", json={"text": reply})
        audio_bytes = tts_res.content
        st.audio(audio_bytes, format="audio/mp3")

    except Exception as e:
        st.error(f"❌ Error: {e}")
