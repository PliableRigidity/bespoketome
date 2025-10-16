import pyaudio
import wave
from faster_whisper import WhisperModel
from ollama import Client
from piper import PiperVoice

# # Record audio from microphone
# p = pyaudio.PyAudio()
# device_index = 1  # change to your mic’s index
# stream = p.open(format=pyaudio.paInt16, channels=1,
#                 rate=16000, input=True,
#                 input_device_index=device_index,
#                 frames_per_buffer=1024)

# frames = []
# for _ in range(0, int(16000 / 1024 * 5)):  # 5 seconds
#     data = stream.read(1024)
#     frames.append(data)
#     print("recording...")

# stream.stop_stream()
# stream.close()
# p.terminate()

# wf = wave.open("output.wav", "wb")
# wf.setnchannels(1)
# wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
# wf.setframerate(16000)
# wf.writeframes(b''.join(frames))
# wf.close()

## Transcribe with Faster Whisper

model_size = "large-v3"       # requires a strong GPU; for lighter try "medium" or "small"
model = WhisperModel(model_size, device="cuda", compute_type="float16")
segments, info = model.transcribe("output.wav", beam_size=5, vad_filter=True)

# segments is a generator; consume once and join
segments_list = list(segments)
final_text = "".join(seg.text for seg in segments_list).strip()

print(f"Detected language '{info.language}' (p={info.language_probability:.3f})")
print("\n--- FINAL TRANSCRIPT ---\n")
print(final_text)

## Generate response with Ollama

client = Client(host='http://127.0.0.1:11434')  # or 'http://localhost:11434'

resp = client.generate(model='llama3.2:latest', prompt=final_text)
print(resp['response'])

## Synthesize speech with Piper

MODEL = r"C:\Piper\models\en-us-ryan-high.onnx"   # change path/voice as needed
OUT_WAV = "tts_output.wav"

# 2) Convert text -> WAV
voice = PiperVoice.load(MODEL, use_cuda=True)
text = resp['response']
voice.synthesize_wav(text, output_file=OUT_WAV)

print(f"Saved: {OUT_WAV}")
