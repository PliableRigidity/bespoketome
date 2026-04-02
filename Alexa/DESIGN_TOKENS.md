# JARVIS UI - Quick Customization Reference

## 🎨 Design Tokens Cheat Sheet

### Primary Colors (Cyan Theme)
```css
--primary: #00f2ff;              /* Main accent - change this for different theme */
--primary-dim: rgba(0, 242, 255, 0.12);
--primary-glow: rgba(0, 242, 255, 0.6);
```

**Examples:**
- Blue theme: `#0088ff`
- Green theme: `#00ff88`
- Orange theme: `#ff8800`
- Red theme: `#ff3366`

### Secondary Colors (Purple Accent)
```css
--accent: #bc13fe;               /* Secondary accent */
--accent-dim: rgba(188, 19, 254, 0.12);
--accent-glow: rgba(188, 19, 254, 0.6);
```

### Background Colors
```css
--bg-deep: #000408;              /* Darkest - main background */
--bg-dark: #0a0e1a;              /* Dark - secondary areas */
--bg-panel: rgba(10, 18, 35, 0.85);   /* Panels with transparency */
--bg-glass: rgba(15, 25, 45, 0.6);    /* Glass effect backgrounds */
```

**Lighter theme:** Increase RGB values by 20-30
**Darker theme:** Decrease RGB values by 10-20

### Text Colors
```css
--text-primary: #e8f4f8;         /* Main text - high contrast */
--text-secondary: #94a3b8;       /* Secondary text - medium contrast */
--text-muted: #64748b;           /* Muted text - low contrast */
```

### Effects
```css
--glow-strength: 8px;            /* Glow blur radius (4-16px) */
--blur-glass: 12px;              /* Glass blur (8-20px) */
```

**Subtle effects:** 4-6px glow, 8-10px blur  
**Strong effects:** 12-16px glow, 16-20px blur

### Spacing Scale
```css
--spacing-xs: 0.25rem;   /* 4px  - tight spacing */
--spacing-sm: 0.5rem;    /* 8px  - small gaps */
--spacing-md: 1rem;      /* 16px - default spacing */
--spacing-lg: 1.5rem;    /* 24px - comfortable spacing */
--spacing-xl: 2rem;      /* 32px - large spacing */
```

### Animation Speeds
```css
--transition-fast: 150ms;        /* Quick interactions */
--transition-normal: 250ms;      /* Default transitions */
--transition-slow: 400ms;        /* Smooth, noticeable */
```

**Snappy feel:** 100-150ms  
**Smooth feel:** 250-350ms  
**Dramatic feel:** 400-600ms

### Layout Dimensions
```css
--nav-width: 80px;               /* Left navigation rail */
--panel-width: 380px;            /* Right evidence panel */
--header-height: 60px;           /* Top header bar */
```

---

## 🚀 Common Customizations

### Make it Brighter
```css
:root {
    --bg-deep: #0a0f1a;          /* Lighter background */
    --bg-dark: #141a2e;
    --text-primary: #ffffff;     /* Pure white text */
}
```

### Make it Darker
```css
:root {
    --bg-deep: #000000;          /* Pure black */
    --bg-dark: #050508;
    --text-primary: #d0d0d0;     /* Slightly dimmed text */
}
```

### Change to Blue Theme
```css
:root {
    --primary: #0088ff;
    --primary-dim: rgba(0, 136, 255, 0.12);
    --primary-glow: rgba(0, 136, 255, 0.6);
}
```

### Change to Green Theme
```css
:root {
    --primary: #00ff88;
    --primary-dim: rgba(0, 255, 136, 0.12);
    --primary-glow: rgba(0, 255, 136, 0.6);
}
```

### Reduce Glow Effects
```css
:root {
    --glow-strength: 4px;        /* Subtle glow */
    --primary-glow: rgba(0, 242, 255, 0.3);  /* Lower opacity */
}
```

### Increase Glow Effects
```css
:root {
    --glow-strength: 16px;       /* Strong glow */
    --primary-glow: rgba(0, 242, 255, 0.8);  /* Higher opacity */
}
```

### Make Panels More Transparent
```css
:root {
    --bg-panel: rgba(10, 18, 35, 0.5);   /* More see-through */
    --bg-glass: rgba(15, 25, 45, 0.3);
}
```

### Make Panels More Opaque
```css
:root {
    --bg-panel: rgba(10, 18, 35, 0.95);  /* Almost solid */
    --bg-glass: rgba(15, 25, 45, 0.8);
}
```

### Wider Navigation
```css
:root {
    --nav-width: 120px;          /* More space for labels */
}
```

### Wider Evidence Panel
```css
:root {
    --panel-width: 480px;        /* More space for content */
}
```

### Faster Animations
```css
:root {
    --transition-fast: 100ms;
    --transition-normal: 180ms;
    --transition-slow: 300ms;
}
```

### Slower Animations
```css
:root {
    --transition-fast: 200ms;
    --transition-normal: 350ms;
    --transition-slow: 500ms;
}
```

---

## 📐 Grid Background

### Current: Subtle Blueprint
```css
background-size: 40px 40px;
opacity: 0.3;
```

### Finer Grid
```css
background-size: 20px 20px;
opacity: 0.2;
```

### Coarser Grid
```css
background-size: 80px 80px;
opacity: 0.4;
```

### No Grid
```css
body::before {
    display: none;
}
```

---

## 🎭 Animation Presets

### Disable All Animations
```javascript
const prefersReducedMotion = true;
```

### Faster Animations Globally
```css
* {
    animation-duration: 0.5s !important;
    transition-duration: 150ms !important;
}
```

### Slower Animations Globally
```css
* {
    animation-duration: 1.5s !important;
    transition-duration: 400ms !important;
}
```

---

## 🔧 Where to Edit

All customizations are in: `templates/index.html`

1. **Design Tokens**: Lines 20-60 (`:root` section)
2. **Colors**: Lines 22-50
3. **Spacing**: Lines 52-56
4. **Effects**: Lines 58-62
5. **Layout**: Lines 64-68

---

## 💡 Pro Tips

1. **Test changes live**: Use browser DevTools to test values before editing file
2. **Keep contrast**: Ensure text remains readable (use contrast checker)
3. **Match glow to color**: Update `--primary-glow` when changing `--primary`
4. **Backup first**: Save a copy before making major changes
5. **Reload page**: Hard refresh (Ctrl+Shift+R) to see changes

---

## 🎨 Preset Themes

### Matrix Green
```css
--primary: #00ff41;
--accent: #00cc33;
--bg-deep: #000000;
--text-primary: #00ff41;
```

### Cyberpunk Pink
```css
--primary: #ff006e;
--accent: #fb5607;
--bg-deep: #03071e;
--text-primary: #ffadda;
```

### Ice Blue
```css
--primary: #00d9ff;
--accent: #0099ff;
--bg-deep: #000814;
--text-primary: #caf0f8;
```

### Sunset Orange
```css
--primary: #ff6b35;
--accent: #f7931e;
--bg-deep: #1a0a00;
--text-primary: #ffe5d9;
```

### Royal Purple
```css
--primary: #9d4edd;
--accent: #c77dff;
--bg-deep: #10002b;
--text-primary: #e0aaff;
```

---

**Quick Edit Location**: `templates/index.html` → `<style>` → `:root { ... }`
