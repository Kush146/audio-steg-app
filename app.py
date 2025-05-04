import streamlit as st
import streamlit.components.v1 as components
from auth import create_users_table, register_user, login_user, get_user_credentials
from steg_utils import hide_message, extract_message
from gtts import gTTS
import tempfile
from pydub import AudioSegment
import io

def convert_audio_to_wav(file):
    audio = AudioSegment.from_file(file)
    wav_io = io.BytesIO()
    audio.export(wav_io, format="wav")
    wav_io.seek(0)
    return wav_io

st.set_page_config(page_title="Audio Steganography AI", page_icon="🎧", layout="centered")
create_users_table()

components.html(open("extra_ui.html", "r").read(), height=0)

# 🌗 Theme Toggle
theme = st.toggle("🌙 Enable Dark Mode", value=True)

if theme:
    bg_color = "#0f172a"
    text_color = "#cbd5e1"
    title_color = "#38bdf8"
    box_bg = "linear-gradient(135deg, rgba(30, 41, 59, 0.95), rgba(15, 23, 42, 0.95))"
    border_color = "rgba(56, 189, 248, 0.3)"
else:
    bg_color = "#f1f5f9"
    text_color = "#1e293b"
    title_color = "#0284c7"
    box_bg = "linear-gradient(135deg, #e0f2fe, #f8fafc)"
    border_color = "#bae6fd"

st.markdown(f"""
    <style>
    body {{
        background-color: {bg_color};
        font-family: 'Segoe UI', sans-serif;
    }}
    .title {{
        font-size: 2.8em;
        font-weight: bold;
        color: {title_color};
        text-align: center;
        margin-top: 2rem;
    }}
    .subtitle {{
        font-size: 1.1em;
        color: {text_color};
        text-align: center;
        margin-bottom: 1rem;
    }}
    .box {{
        background: {box_bg};
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 0 30px rgba(56, 189, 248, 0.25);
        margin-top: 2rem;
        border: 2px solid {border_color};
        backdrop-filter: blur(4px);
        color: {text_color};
    }}
    </style>
""", unsafe_allow_html=True)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_email = ""
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"

def login_ui():
    st.markdown('<div class="title">🎧 Audio Steganography with AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Hide and retrieve secret voice messages inside audio files</div>', unsafe_allow_html=True)
    with st.container():
        with st.form("login_form"):
            st.markdown('<div class="box">', unsafe_allow_html=True)
            email = st.text_input("📧 Email")
            password = st.text_input("🔐 Password", type="password")
            submitted = st.form_submit_button("Login")
            st.markdown('</div>', unsafe_allow_html=True)
            if submitted:
                if login_user(email, password):
                    st.session_state.logged_in = True
                    st.session_state.user_email = email
                    st.success("✅ Logged in!")
                else:
                    st.error("❌ Invalid email or password")

        if st.button("Not registered yet? Create account"):
            st.session_state.auth_mode = "register"
            st.rerun()

def register_ui():
    st.markdown('<div class="title">📝 Create New Account</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Join the platform and start hiding secrets inside audio!</div>', unsafe_allow_html=True)
    with st.container():
        with st.form("register_form"):
            st.markdown('<div class="box">', unsafe_allow_html=True)
            email = st.text_input("📧 New Email")
            password = st.text_input("🔐 New Password", type="password")
            submitted = st.form_submit_button("Register")
            st.markdown('</div>', unsafe_allow_html=True)
            if submitted:
                if register_user(email, password):
                    st.success("✅ Registered! You can now login.")
                    st.session_state.auth_mode = "login"
                    st.rerun()
                else:
                    st.error("⚠️ Email already exists.")

        if st.button("Already have an account? Login"):
            st.session_state.auth_mode = "login"
            st.rerun()

def main_ui():
    st.markdown('<div class="title">🔏 Steganography Control Panel</div>', unsafe_allow_html=True)
    st.markdown(f"""
        <div class='box'>
            <div style='text-align:center'>
                <div class='typewriter'><h2 style='color:{title_color};'>👋 Welcome back, {st.session_state.user_email}</h2></div>
                <p style='color:{text_color}; font-size: 16px;'>
                    You're now in your secure AI dashboard.<br>
                    Start hiding or extracting voice messages from audio files.
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    pin, key = get_user_credentials(st.session_state.user_email)
    st.info(f"🔑 Your Credentials → PIN: `{pin}` | Key: `{key}`")

    choice = st.selectbox("Choose Mode", ["🎙️ Hide Secret Message", "🔍 Extract Hidden Message"])

    if choice == "🎙️ Hide Secret Message":
        uploaded = st.file_uploader("Choose a WAV or MP3 file", type=["wav", "mp3"])
        if uploaded:
            audio = convert_audio_to_wav(uploaded)

            st.subheader("Enter Secret Message")
            message = st.text_area("What message should be hidden?")

            if message and st.button("🔊 Preview Message as Voice"):
                tts = gTTS(text=message, lang='en')
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmpfile:
                    tts.save(tmpfile.name)
                    st.audio(tmpfile.name, format="audio/mp3")

            if st.button("🔐 Generate Stego Audio"):
                if message:
                    stego = hide_message(audio, message, pin, key)
                    st.success("✅ Stego audio created.")
                    st.download_button("⬇️ Download", stego, file_name="stego_output.wav")
                else:
                    st.warning("Please enter a secret message.")

    if choice == "🔍 Extract Hidden Message":
        uploaded_stego = st.file_uploader("Upload audio with hidden message", type=["wav", "mp3"])
        if uploaded_stego:
            stego_audio = convert_audio_to_wav(uploaded_stego)
            user_pin = st.text_input("Enter PIN")
            user_key = st.text_input("Enter Key")
            if st.button("🔓 Extract Message"):
                if user_pin and user_key:
                    result = extract_message(stego_audio.read(), user_pin, user_key)
                    st.success("✅ Extracted Message:")
                    st.code(result)
                else:
                    st.warning("Please provide both PIN and key.")

    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.user_email = ""
        st.rerun()

if st.session_state.logged_in:
    main_ui()
elif st.session_state.auth_mode == "login":
    login_ui()
else:
    register_ui()
