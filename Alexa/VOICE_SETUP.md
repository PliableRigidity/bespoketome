# Voice Assistant Setup Guide

## Overview
The voice assistant feature integrates:
- **OpenWakeWord**: Wake word detection ("Hey Jarvis")
- **Whisper**: Speech-to-text transcription
- **Piper TTS**: Text-to-speech synthesis

## Installation Steps

### 1. Install Python Dependencies

```bash
pip install -r requirements_voice.txt
```

### 2. Install PyAudio (Windows)

PyAudio can be tricky on Windows. Try one of these methods:

**Method 1: Using pipwin**
```bash
pip install pipwin
pipwin install pyaudio
```

**Method 2: Download wheel file**
Download the appropriate `.whl` file from:
https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio

Then install:
```bash
pip install PyAudio‑0.2.13‑cp311‑cp311‑win_amd64.whl
```

### 3. Install Piper TTS

**Windows:**
1. Download Piper from: https://github.com/rhasspy/piper/releases
2. Extract to a folder (e.g., `C:\piper`)
3. Add to PATH or note the location

**Download a Voice Model:**
1. Visit: https://github.com/rhasspy/piper/blob/master/VOICES.md
2. Download a voice model (e.g., `en_US-lessac-medium`)
3. You'll get two files:
   - `en_US-lessac-medium.onnx` (model)
   - `en_US-lessac-medium.onnx.json` (config)

### 4. Configure Piper in Code

Update `web_server.py` or pass model path when starting:

```python
# In the start_voice_assistant endpoint, you can configure:
{
    "piper_model": "C:/path/to/en_US-lessac-medium.onnx",
    "piper_config": "C:/path/to/en_US-lessac-medium.onnx.json"
}
```

## Usage

### Starting the Voice Assistant

1. **Run the web server:**
```bash
python web_server.py
```

2. **Open browser:**
Navigate to `http://localhost:5000`

3. **Switch to Voice tab:**
Click the "🎤 Voice" tab in the header

4. **Start voice assistant:**
Click "Start Voice Assistant"

5. **Activate with wake word:**
Say "Hey Jarvis" to activate listening

6. **Give command:**
After wake word is detected, speak your command

7. **Listen to response:**
Jarvis will respond with synthesized speech

### Voice Flow

```
1. Idle → Listening for "Hey Jarvis"
2. Wake word detected → Recording command (5 seconds)
3. Processing → Transcribing with Whisper
4. Generating response → Using Jarvis backend
5. Speaking → Playing TTS audio
6. Back to listening for wake word
```

## Status Indicators

The voice visualizer shows different states:
- **Idle**: Not running
- **Listening**: Blue pulsing circle - waiting for wake word
- **Recording**: Bright glow - recording your command
- **Processing**: Processing your request
- **Speaking**: Playing audio response

## Troubleshooting

### PyAudio Issues
- **Error: "No module named '_portaudio'"**
  - Reinstall PyAudio using pipwin or wheel file
  
- **Error: "Input overflowed"**
  - Reduce CHUNK size in `voice_module.py`
  - Check microphone settings

### OpenWakeWord Issues
- **Wake word not detected:**
  - Speak clearly and at normal volume
  - Adjust threshold in `voice_module.py` (default: 0.5)
  - Check microphone is working

### Whisper Issues
- **Slow transcription:**
  - Use smaller model: `whisper.load_model("tiny")` or `"base"`
  - Consider using faster-whisper library

### Piper Issues
- **No audio output:**
  - Verify Piper is installed and in PATH
  - Check model paths are correct
  - Test Piper separately: `echo "Hello" | piper --model model.onnx --output_file test.wav`

## Advanced Configuration

### Custom Wake Word

To use a different wake word, download models from:
https://github.com/dscripka/openWakeWord

Update `voice_module.py`:
```python
self.oww_model = Model(wakeword_models=["your_custom_model"], inference_framework="onnx")
```

### Adjust Recording Duration

In `voice_module.py`, modify:
```python
threading.Timer(5.0, self._stop_recording).start()  # Change 5.0 to desired seconds
```

### Change Whisper Model

In `voice_module.py`:
```python
self.whisper_model = whisper.load_model("base")  # Options: tiny, base, small, medium, large
```

## Performance Tips

1. **Use smaller models for faster response:**
   - Whisper: "tiny" or "base"
   - Piper: "low" quality voices

2. **Optimize for your hardware:**
   - GPU acceleration for Whisper (requires CUDA)
   - Adjust audio chunk sizes

3. **Reduce latency:**
   - Use faster-whisper library
   - Pre-load models at startup

## Testing

Test individual components:

```python
# Test wake word detection
from voice_module import VoiceAssistant
va = VoiceAssistant()
va.start()
# Say "Hey Jarvis"

# Test Whisper
import whisper
model = whisper.load_model("base")
result = model.transcribe("test_audio.wav")
print(result["text"])

# Test Piper
# Command line:
echo "Hello world" | piper --model model.onnx --output_file output.wav
```

## Notes

- Voice assistant runs in a separate thread
- WebSocket provides real-time status updates
- All voice interactions are logged in the UI
- Voice and chat interfaces share the same backend (dispatcher)

## Future Enhancements

- [ ] Voice activity detection (VAD) for better command segmentation
- [ ] Continuous conversation mode
- [ ] Multiple wake word support
- [ ] Voice authentication
- [ ] Noise cancellation
- [ ] Custom voice training for Piper
