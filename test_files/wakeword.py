
import os
import sys
import time
import numpy as np
import sounddevice as sd
import openwakeword
from openwakeword.model import Model

# --- Config ---
WAKEWORDS = ["alexa_v0.1", "hey_jarvis_v0.1"]   # choose any that exist after download
SAMPLE_RATE = 16000                   # OWW expects 16kHz mono audio
CHUNK_SEC   = 0.5                     # 0.5s chunks
THRESHOLD   = 0.5                     # detection threshold (lower = more sensitive)

# Helpful: list models directory (for debugging if needed)
RES_DIR = os.path.join(os.path.dirname(openwakeword.__file__), "resources", "models")

def find_model_path(name: str):
    """
    Return a full path to the ONNX model file for a given built-in wakeword name.
    We look for '<name>.onnx' inside OWW's resources folder.
    """
    candidates = [
        os.path.join(RES_DIR, f"{name}.onnx"),
        os.path.join(RES_DIR, f"{name}.ONNX"),
    ]
    for p in candidates:
        if os.path.isfile(p):
            return p
    # fallback: try scanning for similarly named files (robustness across versions)
    if os.path.isdir(RES_DIR):
        for f in os.listdir(RES_DIR):
            if f.lower().startswith(name.lower()) and f.lower().endswith(".onnx"):
                return os.path.join(RES_DIR, f)
    return None

def main():
    # Resolve model file paths
    model_paths = []
    for n in WAKEWORDS:
        p = find_model_path(n)
        if not p:
            print(f"[WARN] Could not find ONNX model for '{n}' in {RES_DIR}")
        else:
            model_paths.append(p)

    if not model_paths:
        print("[ERROR] No ONNX models found. Did you run download_models() successfully?")
        print(f"Checked: {RES_DIR}")
        sys.exit(1)

    print("Using models:")
    for p in model_paths:
        print("  -", os.path.basename(p))

    # Force ONNX backend on Windows
    oww = Model(
        wakeword_models=model_paths,
        inference_framework="onnx"
    )

    # Show what OWW thinks is available
    try:
        print("Available wakewords (backend=onnx):", oww.available_wakewords)
    except Exception:
        pass

    FRAME = int(SAMPLE_RATE * CHUNK_SEC)

    def callback(indata, frames, t, status):
        if status:
            # Status might show xruns etc.
            print(status, flush=True)
        # Convert float32 [-1,1] to int16 PCM
        pcm = (indata[:, 0] * 32768).astype(np.int16)
        scores = oww.predict(pcm)
        for name, prob in scores.items():
            if prob >= THRESHOLD:
                print(f"✅ Wake word: {name}  (score={prob:.2f})", flush=True)

    print("\n🎤 Listening... Say: " + ", ".join(WAKEWORDS))
    print("Press Ctrl+C to stop.\n")

    try:
        with sd.InputStream(
            channels=1,
            samplerate=SAMPLE_RATE,
            blocksize=FRAME,
            dtype="float32",
            callback=callback,
        ):
            while True:
                time.sleep(1.0)
    except KeyboardInterrupt:
        print("\n🛑 Stopped.")
    except Exception as e:
        print("[ERROR]", e)
        print("Tip: If you see an 'errno 13' or file-not-found, print RES_DIR and list files:")
        print("  RES_DIR =", RES_DIR)
        if os.path.isdir(RES_DIR):
            print("  Files:", os.listdir(RES_DIR))

if __name__ == "__main__":
    main()
