import streamlit as st
import asyncio
import edge_tts
from gtts import gTTS
import os

# Page Configuration
st.set_page_config(
    page_title="AI Voice Master Studio",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Custom Premium Styling
st.html("""
    <style>
    .header-box {
        background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%);
        padding: 35px;
        border-radius: 12px;
        text-align: center;
        color: white !important;
        box-shadow: 0 10px 25px rgba(59, 130, 246, 0.25);
        margin-bottom: 25px;
    }
    .header-title {
        font-weight: 800;
        font-size: 2.4em;
        margin-bottom: 8px;
        letter-spacing: -0.5px;
    }
    .header-subtitle {
        font-size: 1.05em;
        opacity: 0.85;
        font-weight: 300;
    }
    .stApp {
        background-color: #FAFBFF;
    }
    div.stContainer {
        background-color: white;
        border-radius: 12px;
        padding: 22px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
        margin-bottom: 20px;
    }
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #1E3A8A 0%, #2563EB 100%) !important;
        color: white !important;
        border-radius: 8px !important;
        font-weight: bold !important;
        font-size: 16px !important;
        padding: 12px 24px !important;
        border: none !important;
        box-shadow: 0 4px 10px rgba(37, 99, 235, 0.2);
    }
    .stSelectbox label, .stTextArea label, .stSlider label {
        font-weight: 600 !important;
        color: #374151 !important;
    }
    .developer-footer {
        text-align: center;
        color: #6B7280;
        font-size: 14px;
        font-weight: 700;
        letter-spacing: 0.5px;
        padding: 15px;
        margin-top: 30px;
        border-top: 1px solid #E5E7EB;
    }
    .card-title {
        color: #4B5563;
        font-weight: 700;
        font-size: 0.95em;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 5px;
    }
    .card-icon {
        font-size: 1.8em;
        margin-bottom: 10px;
    }
    </style>
""")

# Premium Header Box
st.html("""
    <div class="header-box">
        <div class="header-title">🎙️ AI Voice Master Studio</div>
        <div class="header-subtitle">Generate professional voices in Malayalam, Arabic, English & Hindi with studio controls</div>
    </div>
""")

# --- SECTION 1: VOICE CONFIGURATION ---
st.markdown("### 🎚️ 1. Voice & Text Configuration")

with st.container():
    col_v1, col_v2 = st.columns([2, 3])
    
    with col_v1:
        voice_options = {
            "Malayalam - Midhun (Edge - Male)": "edge_ml_midhun",
            "Malayalam - Shobhana (Edge - Female)": "edge_ml_sobhana",
            "Malayalam - Google Voice (gTTS - Female)": "gtts_ml_female",
            "Arabic (Saudi) - Hamed (Edge - Male)": "edge_ar_hamed",
            "Arabic (Saudi) - Zariyah (Edge - Female)": "edge_ar_zariyah",
            "English (US) - Guy (Edge - Male)": "edge_en_guy",
            "English (US) - Ana (Edge - Female)": "edge_en_ana",
            "Hindi - Madhur (Edge - Male)": "edge_hi_madhur",
            "Hindi - Swara (Edge - Female)": "edge_hi_swara"
        }
        selected_voice = st.selectbox("Select Voice Model:", list(voice_options.keys()))
        voice_code = voice_options[selected_voice]

    with col_v2:
        user_text = st.text_area("Enter your script here:", "Hello, welcome to your professional AI Voice Studio. Type any text here to generate high quality audio.", height=100)

# --- SECTION 2: AUDIO STUDIO BOARD ---
st.write("")
st.markdown("### 🎛️ 2. Studio Sound Adjustments")

with st.container():
    c_col1, c_col2 = st.columns(2)
    
    with c_col1:
        with st.container(border=False):
            st.html('<div class="card-title">Voice Speed</div>')
            st.html('<div class="card-icon">⚡</div>')
            voice_speed = st.slider("Speech Rate Change (%)", min_value=-50, max_value=50, value=0, step=5, help="Increase for faster speech, decrease for slower.")

    with c_col2:
        with st.container(border=False):
            st.html('<div class="card-title">Voice Pitch</div>')
            st.html('<div class="card-icon">🎼</div>')
            voice_pitch = st.slider("Pitch Control (Hz)", min_value=-50, max_value=50, value=0, step=5, help="Higher values make voice thinner, lower values make it deeper.")

# --- AUDIO GENERATION FUNCTION ---
async def generate_edge_voice(text, voice_id, speed, pitch, output_path):
    # Formulating edge-tts parameters
    speed_str = f"{'+' if speed >= 0 else ''}{speed}%"
    pitch_str = f"{'+' if pitch >= 0 else ''}{pitch}Hz"
    
    communicate = edge_tts.Communicate(text, voice_id, rate=speed_str, pitch=pitch_str)
    await communicate.save(output_path)

final_audio_path = "studio_voice.mp3"

# --- ACTION BUTTON & PROCESSING ---
st.write("")
if st.button("🎙️ Generate AI Voice", use_container_width=True):
    if user_text:
        with st.spinner("Generating high quality AI Voice..."):
            try:
                # Cleanup existing file if any
                if os.path.exists(final_audio_path):
                    os.remove(final_audio_path)
                    
                # Voice Generation Stage
                if voice_code == "gtts_ml_female":
                    tts = gTTS(text=user_text, lang='ml')
                    tts.save(final_audio_path)
                else:
                    edge_voice_mapping = {
                        "edge_ml_midhun": "ml-IN-MidhunNeural",
                        "edge_ml_sobhana": "ml-IN-SobhanaNeural",
                        "edge_ar_hamed": "ar-SA-HamedNeural",
                        "edge_ar_zariyah": "ar-SA-ZariyahNeural",
                        "edge_en_guy": "en-US-GuyNeural",
                        "edge_en_ana": "en-US-AnaNeural",
                        "edge_hi_madhur": "hi-IN-MadhurNeural",
                        "edge_hi_swara": "hi-IN-SwaraNeural"
                    }
                    selected_edge_id = edge_voice_mapping[voice_code]
                    
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(generate_edge_voice(user_text, selected_edge_id, voice_speed, voice_pitch, final_audio_path))
                
                # Success Display
                st.success("🎉 Voice generated successfully!")
                st.audio(final_audio_path, format="audio/mp3")
                
                with open(final_audio_path, "rb") as f:
                    st.download_button("📥 Download Audio File", f, file_name="ai_studio_voice.mp3", use_container_width=True)
                    
            except Exception as e:
                st.error(f"An error occurred during generation: {e}")
    else:
        st.warning("Please type some text first.")

# --- FOOTER ---
st.html("""
    <div class="developer-footer">
        Created by Ashraf M J
    </div>
""")
