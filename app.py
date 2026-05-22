# 🛠️ Python 3.11+ / Streamlit Cloud ഓഡിയോ എറർ പരിഹരിക്കാനുള്ള പാച്ച്
try:
    import audioop
except ImportError:
    import sys
    try:
        import pyaudioop
        sys.modules['audioop'] = pyaudioop
    except ImportError:
        pass

import streamlit as st
import asyncio
import edge_tts
from gtts import gTTS
import os
from pydub import AudioSegment
from pydub.effects import normalize, compress_dynamic_range

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
        <div class="header-subtitle">Generate professional voices in Malayalam, Arabic, English & Hindi with studio effects</div>
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

# --- SECTION 2: AUDIO MIXING BOARD ---
st.write("")
st.markdown("### 🎛️ 2. Studio Mixing Board")

with st.container():
    c_col1, c_col2 = st.columns(2)
    
    with c_col1:
        with st.container(border=False):
            st.html('<div class="card-title">Depth & Loudness</div>')
            st.html('<div class="card-icon">🔊</div>')
            bass_boost = st.slider("Bass Boost (dB)", min_value=0, max_value=15, value=6, step=1)
            st.write("")
            volume_boost = st.slider("Volume Gain (dB)", min_value=-5, max_value=15, value=3, step=1)

    with c_col2:
        with st.container(border=False):
            st.html('<div class="card-title">Clarity & Echo</div>')
            st.html('<div class="card-icon">✨</div>')
            treble_boost = st.slider("Treble Boost (dB)", min_value=-5, max_value=10, value=2, step=1)
            st.write("")
            reverb_delay = st.slider("Studio Reverb (ms)", min_value=0, max_value=300, value=80, step=20)

    st.write("---")
    enable_compression = st.toggle("Enable Audio Compression (Dynamic Range Balance)", value=True)


# --- AUDIO PRODUCER ENGINE ---
def process_audio(input_path, output_path, bass, treble, volume, delay, compress):
    sound = AudioSegment.from_file(input_path)
    
    if volume != 0:
        sound = sound + volume
        
    if compress:
        sound = compress_dynamic_range(
            sound, 
            threshold=-16.0,
            ratio=3.5,
            attack=10.0,
            release=100.0
        )
        
    if bass > 0:
        bass_filter = sound.low_pass_filter(200)
        sound = sound.overlay(bass_filter + (bass - 2))
        
    if treble != 0:
        treble_filter = sound.high_pass_filter(3000)
        sound = sound.overlay(treble_filter + treble)
        
    if delay > 0:
        decay1 = sound - 9
        decay2 = sound - 16
        sound = sound.overlay(decay1, position=delay)
        sound = sound.overlay(decay2, position=delay * 2)
        
    sound = normalize(sound, headroom=0.5)
    sound.export(output_path, format="mp3", bitrate="192k")

async def generate_edge_voice(text, voice_id, output_path):
    communicate = edge_tts.Communicate(text, voice_id)
    await communicate.save(output_path)

raw_audio_path = "raw_generated.mp3"
final_audio_path = "final_edited_voice.mp3"

# --- ACTION BUTTON & PROCESSING ---
st.write("")
if st.button("🎙️ Generate & Mix Audio", use_container_width=True):
    if user_text:
        with st.spinner("Generating AI Voice & applying studio master effects..."):
            try:
                # 1. Voice Generation Stage
                if voice_code == "gtts_ml_female":
                    tts = gTTS(text=user_text, lang='ml')
                    tts.save(raw_audio_path)
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
                    loop.run_until_complete(generate_edge_voice(user_text, selected_edge_id, raw_audio_path))
                
                # 2. Audio Mastering Stage
                try:
                    process_audio(raw_audio_path, final_audio_path, bass_boost, treble_boost, volume_boost, reverb_delay, enable_compression)
                    audio_to_play = final_edited_voice = final_audio_path
                    st.success("🎉 Voice mastering completed successfully!")
                except Exception as e:
                    audio_to_play = raw_audio_path
                    st.warning("💡 Audio generated in raw format. To apply mixing effects (Bass/Reverb), make sure packages.txt with ffmpeg is configured.")
                
                st.audio(audio_to_play, format="audio/mp3")
                
                with open(audio_to_play, "rb") as f:
                    st.download_button("📥 Download Mastered Audio", f, file_name="ai_studio_voice.mp3", use_container_width=True)
                    
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
