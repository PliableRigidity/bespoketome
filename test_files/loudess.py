import sounddevice as sd
import numpy as np
import time
import sys

# Config
SAMPLERATE = 44100
BLOCK_DURATION = 0.1  # seconds per block (adjust for responsiveness)
CHANNELS = 1

def db_from_block(block):
    # block is float32 in [-1, 1]
    rms = np.sqrt(np.mean(block**2))
    if rms <= 0:
        return -np.inf
    return 20 * np.log10(rms)

def audio_callback(indata, frames, time_info, status):
    if status:
        # You can log status if needed
        pass
    db = db_from_block(indata[:, 0])
    # Print on one line, overwrite (like a live meter)
    meter = "#" * max(0, int((db + 60) / 2))  # simple bar, shift/scale as you like
    sys.stdout.write(f"\rLoudness: {db:6.2f} dB  {meter[:60]:60}")
    sys.stdout.flush()

def main():
    print("Live loudness meter (Ctrl+C to stop)")
    with sd.InputStream(channels=CHANNELS,
                        samplerate=SAMPLERATE,
                        blocksize=int(SAMPLERATE * BLOCK_DURATION),
                        callback=audio_callback):
        while True:
            time.sleep(0.1)  # keep main thread alive

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped.")
