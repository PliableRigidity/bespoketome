# Quick Start Guide - Particle Sphere UI

## Installation

1. **Install Dependencies**
```bash
cd Alexa
.venv\Scripts\activate
pip install -r requirements_voice.txt
```

2. **Start the Server**
```bash
run_web.bat
```
Or manually:
```bash
python web_server.py
```

## Access the UIs

### Particle Sphere Visualization
**URL**: `http://localhost:5000/sphere`

This is the new UI with NO chat interface - just a beautiful 3D particle sphere that reacts to Jarvis's voice.

**Features**:
- 1000 particles in a perfect sphere
- Real-time audio reactivity
- Interactive (drag to rotate)
- Premium visual effects
- Status display
- Command feedback

### Traditional Chat UI
**URL**: `http://localhost:5000/`

The original chat interface with voice assistant integration.

## Usage Flow

1. Open `http://localhost:5000/sphere` in your browser
2. Click "Start Voice Assistant"
3. Wait for "Listening" status
4. Say "Hey Jarvis" to activate
5. Watch the particles react as Jarvis speaks!

## What Makes This Different?

### No Chat Interface
- Pure visualization experience
- No message history
- No text input
- Focus on audio-visual feedback

### Particle Reactivity
The sphere reacts to:
- **Voice Detection**: Gentle pulse when listening
- **Wake Word**: Burst of energy
- **Your Voice**: Moderate reaction while recording
- **Jarvis Speaking**: Maximum reactivity - particles dance to speech amplitude

### Visual States
- **Idle**: Slow rotation, minimal activity
- **Listening**: Gentle pulsing glow
- **Recording**: Increased particle movement
- **Speaking**: Particles expand/contract with audio levels

## Tips for Best Experience

1. **Fullscreen**: Press F11 for immersive view
2. **Dark Room**: Better visual impact
3. **Good Speakers**: Hear Jarvis clearly
4. **Drag to Rotate**: Interact with the sphere
5. **Watch the Stats**: Top-right panel shows live metrics

## Troubleshooting

### "Module not found" errors
```bash
.venv\Scripts\activate
pip install flask flask-socketio python-socketio
```

### Voice assistant not starting
- Check if Piper TTS is installed
- Verify microphone permissions
- See VOICE_SETUP.md for detailed setup

### Particles not reacting
- Ensure voice assistant is started
- Check browser console for WebSocket errors
- Verify audio is playing (Piper must be configured)

## Next Steps

- Configure Piper TTS for speech output (see VOICE_SETUP.md)
- Customize particle colors and count (see SPHERE_README.md)
- Adjust audio sensitivity for your setup

---

**Ready to be amazed? Start the server and open the sphere UI! 🚀**
