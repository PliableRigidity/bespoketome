import sounddevice as sd
import numpy as np
from faster_whisper import WhisperModel
import voice_assistant

# ===== CONFIG =====
DURATION = 5          # seconds per recording
SAMPLE_RATE = 16000   # Whisper-friendly
CHANNELS = 1
MODEL_NAME = "base"   # or "tiny" for faster
COMPUTE_TYPE = "int8" # good for CPU
# ==================

def record_audio():
    print(f"🎙️ Recording for {DURATION} seconds... Speak now.")
    audio = sd.rec(
        int(DURATION * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype="float32"
    )
    sd.wait()
    print("✅ Recording done.")
    return audio[:, 0] if audio.ndim > 1 else audio

def transcribe_audio(model, audio):
    segments, info = model.transcribe(
        audio,
        vad_filter=False,
        beam_size=1,
        temperature=0.0,
        condition_on_previous_text=False
    )
    text = "".join(seg.text for seg in segments).strip()
    if text:
        print("📝 Transcript:", text)
        return text
    else:
        print("🧐 No clear speech detected.")
        return ""

def main():
    print("🧠 Loading Whisper model...")
    model = WhisperModel(MODEL_NAME, compute_type=COMPUTE_TYPE)
    print("✅ Model loaded.\n")

    audio = record_audio()
    _ = transcribe_audio(model, audio)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[EXIT] Stopped manually.")
