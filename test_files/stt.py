import queue
import threading
import numpy as np
import sounddevice as sd
import webrtcvad
import time

from faster_whisper import WhisperModel

SAMPLE_RATE = 16000        # Whisper expects 16 kHz
CHANNELS = 1
FRAME_MS = 20              # 10/20/30ms are valid for WebRTC VAD
FRAME_SAMPLES = SAMPLE_RATE * FRAME_MS // 1000  # 320 samples @ 16kHz for 20ms
VAD_AGGRESSIVENESS = 2     # 0-3 (higher = more aggressive)

# 1) Load Faster-Whisper (choose a model that fits your machine)
# Examples: "tiny", "base", "small", "medium", or GGML/GGUF paths
model = WhisperModel("base", compute_type="int8")  # adjust to your hardware

audio_q = queue.Queue()
vad = webrtcvad.Vad(VAD_AGGRESSIVENESS)

def audio_callback(indata, frames, time_info, status):
    # indata is float32 [-1, 1]; convert to 16-bit PCM mono
    if status:
        # You can log overruns/underruns if needed
        pass
    mono = indata[:, 0] if indata.ndim > 1 else indata
    # chunk into exact 20ms frames for VAD
    buf = (mono * 32768).astype(np.int16)
    # we may receive many samples at once; split into FRAME_SAMPLES
    for start in range(0, len(buf), FRAME_SAMPLES):
        chunk = buf[start:start + FRAME_SAMPLES]
        if len(chunk) == FRAME_SAMPLES:
            audio_q.put(chunk.tobytes())  # VAD expects bytes

def vad_collector():
    """
    Read 20ms frames from the queue, group them into 'utterances' using VAD.
    Yields numpy int16 arrays when speech ends.
    """
    ring = []
    voiced = False
    last_voice_time = 0
    max_silence_after_speech = 0.6  # seconds of silence to end an utterance

    while True:
        try:
            frame = audio_q.get(timeout=0.1)   # 20ms of int16 PCM
        except queue.Empty:
            # If we were speaking and then silence exceeded threshold, flush
            if voiced and (time.time() - last_voice_time > max_silence_after_speech):
                if ring:
                    pcm = b"".join(ring)
                    ring.clear()
                    voiced = False
                    yield np.frombuffer(pcm, dtype=np.int16).astype(np.float32) / 32768.0
            continue

        is_speech = vad.is_speech(frame, SAMPLE_RATE)
        if is_speech:
            voiced = True
            last_voice_time = time.time()
            ring.append(frame)
        else:
            # keep collecting brief silence while in voiced state
            if voiced:
                ring.append(frame)
                # if silence goes too long, we’ll flush in the timeout branch

def transcribe_loop():
    print("🎙️  Speak… (Ctrl+C to stop)")
    for utterance in vad_collector():
        # utterance: float32 mono [-1..1], 16kHz
        # Faster-Whisper accepts numpy arrays directly
        segments, info = model.transcribe(
            utterance,
            beam_size=1,
            vad_filter=False,            # we already did VAD
            temperature=0.0,
            condition_on_previous_text=False
        )
        text = "".join(seg.text for seg in segments).strip()
        if text:
            print("You said:", text)

def main():
    # Start the microphone stream
    with sd.InputStream(
        channels=CHANNELS,
        samplerate=SAMPLE_RATE,
        dtype="float32",
        blocksize=FRAME_SAMPLES,  # align callback with 20 ms frames
        callback=audio_callback,
        latency="low"
    ):
        # Run transcriber in this thread
        transcribe_loop()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nBye!")
