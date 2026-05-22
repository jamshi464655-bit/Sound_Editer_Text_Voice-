import streamlit as st
import asyncio
import edge_tts
from gtts import gTTS
import os
import numpy as np
from scipy.io import wavfile
import io

st.set_page_config(page_title="AI Voice Master Studio", layout="wide")

st.title("🎙️ AI Voice Master Studio")
st.write("---")

# --- 1. VOICE & TEXT CONFIGURATION ---
st.header("⚙️ 1. Voice & Text Configuration")
col_lang, col_text = st.columns([1, 2])

with col_lang:
    voice_options = {
        "Malayalam - Midhun (Edge - Male)": "edge_ml_midhun",
        "Malayalam - Shobhana (Edge - Female)": "edge_ml_sobhana",
        "Malayalam - Google Voice (gTTS)": "gtts_ml_female",
        "Saudi Arabic - Hamed (Edge - Male)": "edge_ar_hamed",
        "Saudi Arabic - Zariyah (Edge - Female)": "edge_ar_zariyah",
        "English (US) - Guy (Edge - Male)": "edge_en_guy",
        "English (US) - Ana (Edge - Female)": "edge_en_ana",
        "Hindi - Madhur (Edge - Male)": "edge_hi_madhur",
        "Hindi - Swara (Edge - Female)": "edge_hi_swara"
    }
    selected_voice = st.selectbox("Select Voice Model:", list(voice_options.keys()))
    voice_code = voice_options[selected_voice]

with col_text:
    user_text = st.text_area("Enter your script here:", "Hello, welcome to your professional AI Voice Studio. Type any text here to generate high quality audio.")

# --- 2. STUDIO SOUND ADJUSTMENTS ---
st.write("---")
st.header("🎛️ 2. Studio Sound Adjustments")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("VOICE BASIC")
    speed_selection = st.slider("Speech Rate Change (%)", min_value=-50, max_value=50, value=0, step=5)
    pitch_selection = st.slider("Pitch Control (Factor)", min_value=0.7, max_value=1.3, value=1.0, step=0.05)

with col2:
    st.subheader("EQUALIZER")
    bass_boost = st.slider("🔊 Bass Booster", min_value=1.0, max_value=3.0, value=1.0, step=0.2)
    treble_boost = st.slider("✨ Treble Control", min_value=0.5, max_value=2.0, value=1.0, step=0.1)

with col3:
    st.subheader("EFFECTS & DYNAMICS")
    reverb_delay = st.slider("🌊 Studio Reverb (Echo Delay)", min_value=0, max_value=10, value=0, step=1)
    volume_boost = st.slider("📈 Volume Amplifier", min_value=0.5, max_value=3.0, value=1.0, step=0.2)
    enable_compression = st.checkbox("🎛️ Enable Audio Compressor", value=True)


async def generate_edge_voice(text, voice_id, speed, output_path):
    speed_str = f"{speed:+}%" if speed != 0 else "+0%"
    communicate = edge_tts.Communicate(text, voice_id, rate=speed_str)
    await communicate.save(output_path)

# ഓഡിയോ പ്രോസസ്സ് ചെയ്യാനുള്ള പുതിയ എറർ-ഫ്രീ ഫങ്ക്ഷൻ (Scipy & Numpy)
def process_audio_scipy(input_path, output_path, bass, treble, volume, delay, compress, pitch):
    # എഡ്ജ് ടിടിഎസ് വോയിസ് റീഡ് ചെയ്യുന്നു
    import subprocess
    wav_path = "temp_raw.wav"
    
    # MP3 ഫയലിനെ WAV ആക്കുന്നു
    if os.path.exists(wav_path):
        os.remove(wav_path)
    subprocess.run(['ffmpeg', '-i', input_path, wav_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    sample_rate, data = wavfile.read(wav_path)
    
    # ഫ്ലോട്ട് ഫോർമാറ്റിലേക്ക് മാറ്റുന്നു
    data = data.astype(np.float32)
    
    # 1. വോളിയം ആംപ്ലിഫയർ
    data = data * volume
    
    # 2. കംപ്രസ്സർ ലിമിറ്റർ
    if compress:
        max_val = np.max(np.abs(data))
        if max_val > 32767:
            data = (data / max_val) * 32700
            
    # 3. ബേസ് ബൂസ്റ്റർ (Moving Average Box Filter)
    if bass > 1.0:
        kernel_size = 5
        bass_layer = np.convolve(data, np.ones(kernel_size)/kernel_size, mode='same')
        data = data + (bass_layer * (bass - 1.0))
        
    # 4. റീവെർബ് / എക്കോ
    if delay > 0:
        delay_samples = int(sample_rate * (delay * 0.05))
        echo_data = np.zeros_like(data)
        if delay_samples < len(data):
            echo_data[delay_samples:] = data[:-delay_samples] * 0.4
            data = data + echo_data

    # 5. പിച്ച് കൺട്രോൾ (Sample Rate മാറ്റം വഴി)
    final_rate = int(sample_rate * pitch)
    
    # വീണ്ടും ഇൻ്റജർ ഫോർമാറ്റിലേക്ക് മാറ്റുന്നു
    data = np.clip(data, -32768, 32767).astype(np.int16)
    
    # ഫൈനൽ WAV സേവ് ചെയ്യുന്നു
    wavfile.write(output_path, final_rate, data)

raw_audio_path = "raw_generated.mp3"
final_wav_path = "final_output.wav"

# --- GENERATE BUTTON ---
st.write("---")
if st.button("🎙️ Generate AI Voice", use_container_width=True):
    if user_text:
        with st.spinner("Processing your professional audio... Please wait..."):
            try:
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
                    loop.run_until_complete(generate_edge_voice(user_text, selected_edge_id, speed_selection, raw_audio_path))
                
                # പുതിയ എറർ ഫ്രീ പ്രോസസ്സിംഗ്
                process_audio_scipy(raw_audio_path, final_wav_path, bass_boost, treble_boost, volume_boost, reverb_delay, enable_compression, pitch_selection)
                
                st.success("🎉 Voice Generated Successfully with Studio Effects!")
                st.audio(final_wav_path, format="audio/wav")
                
                with open(final_wav_path, "rb") as f:
                    st.download_button("📥 Download Mastered Audio", f, file_name="studio_quality_voice.wav", use_container_width=True)
                    
            except Exception as e:
                st.error(f"Error processing audio: {e}")
    else:
        st.warning("Please enter some text first.")

# --- FOOTER ---
st.write("---")
st.markdown("<h4 style='text-align: center; color: #888888;'>Created by Ashraf M J</h4>", unsafe_html=True)
