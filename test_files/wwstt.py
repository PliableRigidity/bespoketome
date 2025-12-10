import os
import sys
import time
import numpy as np
import sounddevice as sd
import openwakeword
from openwakeword.model import Model
import stt

# --- Config ---
WAKEWORDS = ["alexa_v0.1", "hey_jarvis_v0.1"]   # must exist in OWW models
SAMPLE_RATE = 16000
CHUNK_SEC   = 0.5
THRESHOLD   = 0.5

RES_DIR = os.path.join(os.path.dirname(openwakeword.__file__), "resources", "models")


def find_model_path(name: str):
    """
    Find ONNX file path for a given wakeword name.
    """
    candidates = [
        os.path.join(RES_DIR, f"{name}.onnx"),
        os.path.join(RES_DIR, f"{name}.ONNX"),
    ]
    for p in candidates:
        if os.path.isfile(p):
            return p

    if os.path.isdir(RES_DIR):
        for f in os.listdir(RES_DIR):
            if f.lower().startswith(name.lower()) and f.lower().endswith(".onnx"):
                return os.path.join(RES_DIR, f)

    return None


def listen_for_wakeword(oww):
    """
    Block until a wake word is detected (True) or user stops / error occurs (False).
    Uses a fresh openwakeword Model instance passed in.
    """
    FRAME = int(SAMPLE_RATE * CHUNK_SEC)
    triggered = {"value": False}

    def callback(indata, frames, t, status):
        if status:
            print(status, flush=True)
        if triggered["value"]:
            return  # already triggered, ignore

        # float32 [-1,1] -> int16
        pcm = (indata[:, 0] * 32768).astype(np.int16)
        scores = oww.predict(pcm)

        for name, prob in scores.items():
            if prob >= THRESHOLD:
                print(f"✅ Wake word detected: {name} (score={prob:.2f})", flush=True)
                triggered["value"] = True
                return

    print("🎤 Listening for wake word:", ", ".join(WAKEWORDS))

    try:
        with sd.InputStream(
            channels=1,
            samplerate=SAMPLE_RATE,
            blocksize=FRAME,
            dtype="float32",
            callback=callback,
        ):
            while not triggered["value"]:
                time.sleep(0.05)
    except KeyboardInterrupt:
        print("\n🛑 Stopped by user while listening.")
        return False
    except Exception as e:
        print("[ERROR] Audio error while listening:", e)
        return False

    return triggered["value"]


def main():
    # ---- Resolve model paths once ----
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

    print("Using wakeword models:")
    for p in model_paths:
        print("  -", os.path.basename(p))

    print("\nReady. Say a wake word to start STT. Ctrl+C to exit.\n")

    try:
        while True:
            # 👉 Create a *fresh* wakeword model each cycle to avoid residual state
            oww = Model(
                wakeword_models=model_paths,
                inference_framework="onnx"
            )

            try:
                print("Available wakewords:", oww.available_wakewords)
            except Exception:
                pass

            triggered = listen_for_wakeword(oww)
            if not triggered:
                # user stopped or error
                break

            print("\n🎯 Wake word confirmed. Starting STT...\n")
            stt.main()  # one-shot record + transcribe
            print("\n↩️ Returning to wake word listening...\n")

            # Optional tiny pause before next cycle
            time.sleep(0.2)

    except KeyboardInterrupt:
        print("\n🛑 Exiting main loop.")


if __name__ == "__main__":
    main()
