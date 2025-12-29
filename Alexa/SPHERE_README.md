# JARVIS Particle Sphere Visualization

A stunning 3D particle sphere visualization that reacts in real-time to Jarvis's voice output.

## Features

### Visual Design
- **1000 Particles**: Arranged in a perfect sphere using Fibonacci distribution for even spacing
- **3D Rotation**: Particles continuously rotate in 3D space
- **Audio Reactivity**: Particles expand and pulse based on Jarvis's speech amplitude
- **Smooth Animations**: Fluid transitions and movements
- **Interactive**: Drag to rotate the sphere manually
- **Premium Aesthetics**: Glassmorphism, gradients, and dynamic lighting effects

### Real-Time Integration
- **WebSocket Connection**: Live updates from the voice assistant
- **Audio Level Analysis**: Real-time RMS calculation of speech output
- **Status Synchronization**: Visual feedback for all voice assistant states
- **Command Display**: Shows what you said and Jarvis's response

### Voice States
The sphere reacts differently to each state:
- **Idle**: Minimal movement, low reactivity
- **Listening**: Gentle pulsing, waiting for wake word
- **Wake Word Detected**: Burst of activity
- **Recording**: High reactivity to your voice
- **Processing**: Medium activity while thinking
- **Speaking**: Maximum reactivity, particles dance to Jarvis's voice

## How to Use

### 1. Start the Server
```bash
run_web.bat
```

### 2. Open the Sphere UI
Navigate to: `http://localhost:5000/sphere`

### 3. Activate Voice Assistant
Click the "Start Voice Assistant" button

### 4. Interact
- Say "Hey Jarvis" to activate
- Watch the particles react to the conversation
- Drag the sphere to rotate it manually

## Technical Details

### Particle System
- **Distribution**: Fibonacci sphere algorithm for uniform particle placement
- **Rendering**: HTML5 Canvas with 2D context
- **Animation**: RequestAnimationFrame for smooth 60fps
- **Depth Sorting**: Z-index based rendering for proper 3D effect

### Audio Analysis
- **RMS Calculation**: Root Mean Square of audio samples
- **Normalization**: Scaled to 0-1 range for consistent visualization
- **Smoothing**: Exponential smoothing for fluid transitions
- **Real-time**: Updates during TTS playback at ~60Hz

### Performance
- **Optimized Rendering**: Only redraws when needed
- **Efficient Sorting**: Quick sort for depth ordering
- **Low Latency**: WebSocket for instant updates
- **Responsive**: Adapts to window size

## Customization

### Particle Count
Edit `sphere.html` line ~485:
```javascript
const particleCount = 1000; // Change this number
```

### Colors
Edit the color palette in `sphere.html` line ~508:
```javascript
const colors = [
    'rgba(0, 212, 255, 0.8)',   // Primary cyan
    'rgba(124, 58, 237, 0.8)',  // Accent purple
    // Add more colors here
];
```

### Reactivity
Adjust sensitivity in `sphere.html` line ~511:
```javascript
this.reactivity = 0.5 + Math.random() * 0.5; // 0.5-1.0 range
```

### Audio Threshold
Modify normalization in `voice_module.py` line ~358:
```python
normalized_level = min(rms / 3000.0, 1.0)  # Adjust 3000.0
```

## Comparison with Chat UI

| Feature | Chat UI | Sphere UI |
|---------|---------|-----------|
| **Purpose** | Text conversation | Visual feedback |
| **Chat History** | ✅ Yes | ❌ No |
| **Voice Assistant** | ✅ Yes | ✅ Yes |
| **Visualization** | Basic status | 3D particle sphere |
| **Audio Reactivity** | ❌ No | ✅ Yes |
| **Saved Chats** | ✅ Yes | ❌ No |
| **Best For** | Conversations | Presentations/Demos |

## Browser Compatibility

- ✅ Chrome/Edge (Recommended)
- ✅ Firefox
- ✅ Safari
- ⚠️ Older browsers may have reduced performance

## Performance Tips

1. **Reduce Particles**: Lower particle count for slower systems
2. **Close Other Tabs**: Free up browser resources
3. **Hardware Acceleration**: Enable in browser settings
4. **Fullscreen Mode**: Press F11 for immersive experience

## Troubleshooting

### Particles Not Moving
- Check if voice assistant is started
- Verify WebSocket connection in browser console
- Ensure server is running

### Low Frame Rate
- Reduce particle count
- Close resource-intensive applications
- Try a different browser

### No Audio Reactivity
- Verify Piper TTS is configured
- Check audio_level_callback is set
- Look for errors in server console

## Future Enhancements

Potential improvements:
- [ ] Multiple visualization modes (cube, spiral, etc.)
- [ ] Color themes
- [ ] Particle trails
- [ ] Beat detection for music
- [ ] VR/AR support
- [ ] Export as video/GIF
- [ ] Frequency spectrum visualization
- [ ] Custom particle shapes

## Credits

Built with:
- HTML5 Canvas
- Socket.IO for WebSockets
- Fibonacci Sphere Algorithm
- Modern CSS (Glassmorphism)
- Vanilla JavaScript (No frameworks!)

---

**Enjoy the show! 🎨✨**
