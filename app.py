import streamlit as st
import asyncio
import edge_tts
from gtts import gTTS
import os
from pydub import AudioSegment
from pydub.effects import normalize, compress_dynamic_range

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

# നിങ്ങളുടെ നിലവിലുള്ള Speed, Pitch എന്നിവയ്ക്കൊപ്പം പുതിയ എഫക്റ്റുകളും കോളങ്ങളായി തിരിക്കുന്നു
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("VOICE BASIC")
    # 1. സ്പീഡ്
    speed_selection = st.slider("Speech Rate Change (%)", min_value=-50, max_value=50, value=0, step=5)
    # 2. പിച്ച് (Pydub-ൽ പിച്ച് മാറ്റം സാമ്പിൾ റേറ്റ് വഴിയാണ് ചെയ്യുക)
    pitch_selection = st.slider("Pitch Control (Hz)", min_value=-5, max_value=5, value=0, step=1)

with col2:
    st.subheader("EQUALIZER")
    # 3. ബേസ് ബൂസ്റ്റർ (Bass)
    bass_boost = st.slider("🔊 Bass Booster (dB)", min_value=0, max_value=15, value=6, step=1)
    # 4. ട്രെബിൾ (Treble)
    treble_boost = st.slider("✨ Treble Control (dB)", min_value=-5, max_value=10, value=2, step=1)

with col3:
    st.subheader("EFFECTS & DYNAMICS")
    # 5. റീവെർബ് (Reverb/Echo)
    reverb_delay = st.slider("🌊 Studio Reverb (Echo ms)", min_value=0, max_value=300, value=80, step=20)
    # 6. വോളിയം ആംപ്ലിഫയർ
    volume_boost = st.slider("📈 Volume Amplifier (dB)", min_value=-5, max_value=15, value=3, step=1)
    # 7. കംപ്രസ്സർ (Compressor)
    enable_compression = st.checkbox("🎛️ Enable Audio Compressor", value=True)


# --- AUDIO PROCESSING LOGIC ---
raw_audio_path = "raw_generated.mp3"
final_audio_path = "final_edited_voice.mp3"

async def generate_edge_voice(text, voice_id, speed):
    # Speed പെർസന്റേജ് അഡ്ജസ്റ്റ് ചെയ്യുന്നു
    speed_str = f"{speed:+}%" if speed != 0 else "+0%"
    communicate = edge_tts.Communicate(text, voice_id, rate=speed_str)
    await communicate.save(raw_audio_path)

def process_audio(input_path, output_path, bass, treble, volume, delay, compress, pitch):
    sound = AudioSegment.from_file(input_path)
    
    # 1. വോളിയം ആംപ്ലിഫയർ
    if volume != 0:
        sound = sound + volume
        
    # 2. പിച്ച് കൺട്രോൾ
    if pitch != 0:
        new_sample_rate = int(sound.frame_rate * (2.0 ** (pitch / 12.0)))
        sound = sound._spawn(sound.raw_data, overrides={'frame_rate': new_sample_rate})
        sound = sound.set_frame_rate(sound.frame_rate)
        
    # 3. കംപ്രസ്സർ ആക്റ്റിവേഷൻ
    if compress:
        sound = compress_dynamic_range(sound, threshold=-20.0, ratio=4.0, attack=5.0, release=50.0)
        
    # 4. ബേസ് ബൂസ്റ്റർ
    if bass > 0:
        lows = sound.low_pass_filter(250)
        sound = sound.overlay(lows + bass)
        
    # 5. ട്രെബിൾ കൺട്രോൾ
    if treble != 0:
        highs = sound.high_pass_filter(2000)
        sound = sound.overlay(highs + treble)
        
    # 6. റീവെർബ് / എക്കോ
    if delay > 0:
        echo = sound - 6
        sound = sound.overlay(echo, position=delay)
        
    # നോർമലൈസേഷൻ
    sound = normalize(sound)
    sound.export(output_path, format="mp3")


# --- GENERATE BUTTON ---
st.write("---")
if st.button("🎙️ Generate AI Voice", use_container_width=True):
    if user_text:
        with st.spinner("Processing your professional audio... Please wait..."):
            try:
                # TTS ജനറേഷൻ
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
                    loop.run_until_complete(generate_edge_voice(user_text, selected_edge_id, speed_selection))
                
                # പ്രൊഫഷണൽ എഡിറ്റിംഗ് എഫക്റ്റുകൾ നൽകുന്നു
                process_audio(raw_audio_path, final_audio_path, bass_boost, treble_boost, volume_boost, reverb_delay, enable_compression, pitch_selection)
                
                st.success("🎉 Voice Generated Successfully with Studio Effects!")
                st.audio(final_audio_path, format="audio/mp3")
                
                with open(final_audio_path, "rb") as f:
                    st.download_button("📥 Download Mastered Audio", f, file_name="studio_quality_voice.mp3", use_container_width=True)
                    
            except Exception as e:
                st.error(f"Error processing audio: {e}")
    else:
        st.warning("Please enter some text first.")

# --- FOOTER ---
st.write("---")
st.markdown("<h4 style='text-align: center; color: #888888;'>Created by Ashraf M J</h4>", unsafe_html=True)
