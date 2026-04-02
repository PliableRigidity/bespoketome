# JARVIS Command Deck UI - Design Documentation

## Overview

The JARVIS interface has been completely redesigned as a futuristic engineering "command deck" with a focus on:
- **Aesthetic**: Dark, futuristic, engineering-centered design
- **Animations**: Smooth, tasteful anime.js animations
- **Functionality**: Three-panel layout with navigation, chat, and evidence
- **Responsiveness**: Desktop-first, mobile-friendly

---

## Layout Structure

```
┌─────────────────────────────────────────────────────────┐
│  [Nav Rail]  │  [Main Content]  │  [Evidence Panel]    │
│              │                   │                       │
│   J          │  ┌─ Header ─────┐│  Evidence & Visuals  │
│              │  │ JARVIS        ││                       │
│  💬 Chat     │  └──────────────┘│  📷 Images           │
│  ✓ Tasks     │                   │  📚 Sources          │
│  🧠 Memory   │  [Messages Area]  │  🔧 Debug            │
│  🔍 Retrieval│                   │                       │
│  ⚙️ Systems  │                   │                       │
│  🤖 Robots   │  [Input Area]     │                       │
│              │  Ask Jarvis…      │                       │
└─────────────────────────────────────────────────────────┘
```

### Components

1. **Left Navigation Rail** (80px width)
   - Logo at top
   - 6 module icons (Chat, Tasks, Memory, Retrieval, Systems, Robots)
   - Only Chat is functional; others show "Coming Soon" cards
   - Hover animations: glow + slide

2. **Main Content Area** (flexible)
   - Header with title and status indicator
   - Messages area with chat bubbles
   - Input area with quick actions and command bar

3. **Right Evidence Panel** (380px width)
   - Displays images, sources, and debug info
   - Staggered animations on content load
   - Scrollable sections

---

## Design Tokens

All design values are defined in CSS custom properties for easy customization:

### Colors
```css
--bg-deep: #000408;           /* Main background */
--bg-dark: #0a0e1a;           /* Secondary background */
--bg-panel: rgba(10, 18, 35, 0.85);  /* Panel backgrounds */
--bg-glass: rgba(15, 25, 45, 0.6);   /* Glass effect */

--primary: #00f2ff;           /* Cyan accent */
--primary-dim: rgba(0, 242, 255, 0.12);
--primary-glow: rgba(0, 242, 255, 0.6);

--accent: #bc13fe;            /* Purple accent */
--accent-dim: rgba(188, 19, 254, 0.12);
--accent-glow: rgba(188, 19, 254, 0.6);

--success: #00ff88;           /* Green for status */
--warning: #ffaa00;           /* Orange for warnings */
--error: #ff3366;             /* Red for errors */

--text-primary: #e8f4f8;      /* Main text */
--text-secondary: #94a3b8;    /* Secondary text */
--text-muted: #64748b;        /* Muted text */

--border: rgba(0, 242, 255, 0.2);
--border-subtle: rgba(0, 242, 255, 0.08);
```

### Spacing
```css
--spacing-xs: 0.25rem;   /* 4px */
--spacing-sm: 0.5rem;    /* 8px */
--spacing-md: 1rem;      /* 16px */
--spacing-lg: 1.5rem;    /* 24px */
--spacing-xl: 2rem;      /* 32px */
```

### Effects
```css
--glow-strength: 8px;           /* Glow blur radius */
--blur-glass: 12px;             /* Glass blur amount */
--transition-fast: 150ms;       /* Fast transitions */
--transition-normal: 250ms;     /* Normal transitions */
--transition-slow: 400ms;       /* Slow transitions */
```

### Layout
```css
--nav-width: 80px;              /* Navigation rail width */
--panel-width: 380px;           /* Evidence panel width */
--header-height: 60px;          /* Header height */
```

---

## Animations

All animations use **anime.js** and respect `prefers-reduced-motion`.

### Navigation Items
- **Hover**: Glow pulse + 4px slide right
- **Click**: Scale down/up effect
- **Duration**: 250ms

```javascript
anime({
    targets: navItem,
    translateX: [0, 4],
    boxShadow: ['0 0 0px rgba(0, 242, 255, 0)', '0 0 12px rgba(0, 242, 255, 0.4)'],
    duration: 250,
    easing: 'easeOutQuad'
});
```

### Message Entry
- **Effect**: Fade up + blur to sharp
- **Duration**: 450ms
- **Easing**: easeOutExpo

```javascript
anime({
    targets: message,
    translateY: [20, 0],
    opacity: [0, 1],
    filter: ['blur(4px)', 'blur(0px)'],
    duration: 450,
    easing: 'easeOutExpo'
});
```

### Evidence Panel Items
- **Effect**: Staggered fade-in from right
- **Delay**: 60-80ms per item
- **Duration**: 350-400ms

```javascript
anime({
    targets: item,
    translateX: [20, 0],
    opacity: [0, 1],
    delay: index * 60,
    duration: 350,
    easing: 'easeOutExpo'
});
```

### Image Cards
- **Hover**: Tiny 3D tilt + glow
- **Duration**: 300ms

```javascript
anime({
    targets: imageCard,
    rotateY: [0, 5],
    rotateX: [0, -5],
    duration: 300,
    easing: 'easeOutQuad'
});
```

---

## Features

### Chat Interface
- **User messages**: Right-aligned, purple accent
- **Assistant messages**: Left-aligned, cyan accent
- **Badges**: Show image/source counts, clickable to scroll to panel
- **Markdown support**: Via marked.js
- **Code blocks**: Styled with dark background

### Quick Actions
Four preset commands above input:
1. Summarize
2. Show Sources
3. Show Images
4. Debug

### Evidence Panel

#### Images Section
- Grid layout (auto-fill, min 150px)
- Thumbnail preview with overlay on hover
- Click to open full image in new tab
- Graceful error handling (SVG placeholder)

#### Sources Section
- List of clickable source cards
- Title, snippet, and URL
- Hover effect with glow

#### Debug Section
- Only shown if debug data exists
- Timeline-style display
- Monospace font for technical data

### Input Area
- Auto-resizing textarea (max 120px)
- Placeholder: "Ask Jarvis…"
- Enter to send, Shift+Enter for newline
- Send button with hover glow

---

## Customization Guide

### Change Theme Colors

Edit the `:root` variables in the `<style>` section:

```css
:root {
    --primary: #00f2ff;  /* Change to your preferred accent color */
    --accent: #bc13fe;   /* Change to your secondary accent */
    --bg-deep: #000408;  /* Change background darkness */
}
```

### Adjust Glow Intensity

```css
:root {
    --glow-strength: 8px;  /* Increase for stronger glow */
}
```

### Change Panel Widths

```css
:root {
    --nav-width: 80px;      /* Navigation rail */
    --panel-width: 380px;   /* Evidence panel */
}
```

### Disable Animations

Animations automatically disable if user has `prefers-reduced-motion` enabled. To force disable:

```javascript
const prefersReducedMotion = true;  // Set to true
```

---

## Module System

### Active Modules
- **Chat**: Fully functional

### Coming Soon Modules
- **Tasks**: Task management placeholder
- **Memory**: Long-term memory placeholder
- **Retrieval**: Advanced search placeholder
- **Systems**: System control placeholder
- **Robots**: Robotics interface placeholder

To activate a module, implement its view and update the navigation handler.

---

## Response Schema

The UI expects responses in this format:

```json
{
  "text": "Answer text here...",
  "images": [
    {
      "title": "Image title",
      "image_url": "https://...",
      "thumbnail_url": "https://...",
      "source_url": "https://..."
    }
  ],
  "sources": [
    {
      "title": "Source title",
      "url": "https://...",
      "snippet": "Preview text..."
    }
  ],
  "debug": {
    "tool": "web_search",
    "duration_ms": 1234
  }
}
```

**Backward compatibility**: String responses are automatically converted.

---

## Running the UI

### Start Server
```bash
cd Alexa
.\run_web.bat
```

### Access
Open browser to: **http://localhost:5000**

### Test Queries
- `"show me a cat"` → Images
- `"who is elon musk"` → Text + Images + Sources
- `"what is quantum computing"` → Text + Sources

---

## Browser Support

- **Chrome/Edge**: Full support
- **Firefox**: Full support
- **Safari**: Full support (may need prefixes for some effects)
- **Mobile**: Responsive layout (panel collapses on mobile)

---

## Performance

- **Animations**: GPU-accelerated transforms
- **Reduced motion**: Automatic detection and disable
- **Lazy loading**: Images load on demand
- **Efficient rendering**: Minimal DOM manipulation

---

## Accessibility

- **Keyboard navigation**: Full support
- **Screen readers**: Semantic HTML
- **Focus indicators**: Visible focus rings
- **Color contrast**: WCAG AA compliant
- **Reduced motion**: Respects user preference

---

## File Structure

```
templates/
  index.html          # Complete UI (single file)
```

All styles and scripts are inline for simplicity. For production, consider splitting into:
- `static/css/jarvis.css`
- `static/js/jarvis.js`

---

## Troubleshooting

### Animations not working
- Check browser console for errors
- Verify anime.js is loaded
- Check `prefersReducedMotion` setting

### Panel not showing content
- Verify response schema matches expected format
- Check browser console for errors
- Ensure `updateEvidencePanel()` is called

### Layout issues
- Clear browser cache
- Check viewport width (min 768px recommended)
- Verify CSS custom properties are supported

---

## Future Enhancements

- [ ] Voice input integration
- [ ] Drag-and-drop file upload
- [ ] Multi-user chat rooms
- [ ] Theme switcher (light/dark)
- [ ] Customizable quick actions
- [ ] Export chat history
- [ ] Keyboard shortcuts panel

---

## Credits

- **Fonts**: Inter, Orbitron (Google Fonts)
- **Animations**: anime.js by Julian Garnier
- **Markdown**: marked.js
- **Icons**: Unicode emoji (no external dependencies)

---

**Version**: 2.0  
**Last Updated**: 2026-02-12  
**License**: MIT
