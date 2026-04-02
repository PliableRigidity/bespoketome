# VECTOR Command Center - Design System

## 🎨 Color Tokens

### Primary Colors
```css
--primary: #00f2ff;           /* Cyan - Main accent */
--primary-dark: #0088cc;      /* Darker cyan */
--primary-dim: rgba(0, 242, 255, 0.1);
--primary-glow: rgba(0, 242, 255, 0.5);

--accent: #a855f7;            /* Violet - Secondary accent */
--accent-dim: rgba(168, 85, 247, 0.1);

--electric: #3b82f6;          /* Electric blue */
```

### Status Colors
```css
--success: #00ff88;           /* Green */
--warning: #ffaa00;           /* Orange */
--error: #ff4444;             /* Red */
--info: #00d4ff;              /* Light cyan */
```

### Background Colors
```css
--bg-deep: #0a0e1a;           /* Deepest background */
--bg-dark: #0f1419;           /* Main background */
--bg-panel: rgba(15, 20, 25, 0.95);  /* Panel background */
--bg-glass: rgba(255, 255, 255, 0.03);  /* Glass cards */
--bg-hover: rgba(255, 255, 255, 0.05);
```

### Border & Text
```css
--border: rgba(255, 255, 255, 0.1);
--border-subtle: rgba(255, 255, 255, 0.05);
--border-bright: rgba(0, 242, 255, 0.3);

--text-primary: #ffffff;
--text-secondary: #b0b0b0;
--text-muted: #666666;
```

## 📐 Layout Structure

```
┌─────────────────────────────────────────────────────────────┐
│  HEADER (System Status, Time, Indicators)                   │
├──────┬──────────────────────────────────────┬───────────────┤
│      │                                      │               │
│  S   │         MAIN PANEL                   │   CONTEXT     │
│  I   │      (Active Module View)            │   PANEL       │
│  D   │                                      │               │
│  E   │                                      │  - Evidence   │
│  B   │                                      │  - Logs       │
│  A   │                                      │  - Status     │
│  R   │                                      │               │
│      │                                      │               │
├──────┴──────────────────────────────────────┴───────────────┤
│  COMMAND BAR (Quick Actions, Input)                         │
└─────────────────────────────────────────────────────────────┘
```

## 🎭 Typography

### Font Families
```css
--font-ui: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
--font-mono: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace;
--font-display: 'Orbitron', monospace;  /* For headers */
```

### Font Sizes
```css
--text-xs: 0.75rem;    /* 12px */
--text-sm: 0.875rem;   /* 14px */
--text-base: 1rem;     /* 16px */
--text-lg: 1.125rem;   /* 18px */
--text-xl: 1.25rem;    /* 20px */
--text-2xl: 1.5rem;    /* 24px */
--text-3xl: 1.875rem;  /* 30px */
```

## 🌊 Animations

### Timing Functions
```css
--ease-smooth: cubic-bezier(0.4, 0, 0.2, 1);
--ease-bounce: cubic-bezier(0.68, -0.55, 0.265, 1.55);
--ease-in-out: cubic-bezier(0.4, 0, 0.6, 1);
```

### Durations
```css
--duration-fast: 150ms;
--duration-normal: 300ms;
--duration-slow: 500ms;
```

### Keyframes
- `fadeIn` - Opacity 0 → 1
- `slideUp` - TranslateY(20px) → 0
- `slideDown` - TranslateY(-20px) → 0
- `scaleIn` - Scale(0.95) → 1
- `pulse` - Subtle glow pulse
- `shimmer` - Loading shimmer effect

## 🎯 Component Patterns

### Glass Card
```css
background: var(--bg-glass);
backdrop-filter: blur(10px);
border: 1px solid var(--border);
border-radius: 12px;
box-shadow: 0 4px 24px rgba(0, 0, 0, 0.3);
```

### Glow Effect
```css
box-shadow: 0 0 20px var(--primary-glow);
```

### Hover Lift
```css
transform: translateY(-2px);
box-shadow: 0 8px 32px rgba(0, 242, 255, 0.2);
```

## 📱 Responsive Breakpoints

```css
--breakpoint-sm: 640px;
--breakpoint-md: 768px;
--breakpoint-lg: 1024px;
--breakpoint-xl: 1280px;
--breakpoint-2xl: 1536px;
```

## 🎨 Module-Specific Colors

### Tasks
- High Priority: `--error` (red)
- Medium Priority: `--warning` (orange)
- Low Priority: `--success` (green)
- Completed: `--text-muted` (gray)

### Memory
- User Memory: `--primary` (cyan)
- Assistant Memory: `--accent` (violet)
- Pinned: `--warning` (orange star)

### Systems
- Online: `--success` (green)
- Warning: `--warning` (orange)
- Offline: `--error` (red)
- Unknown: `--text-muted` (gray)

### Robots
- Active: `--success` (green)
- Idle: `--info` (cyan)
- Error: `--error` (red)
- E-STOP: `--error` (red, pulsing)

## 🌟 Special Effects

### Blueprint Grid Background
```css
background-image: 
  linear-gradient(var(--border-subtle) 1px, transparent 1px),
  linear-gradient(90deg, var(--border-subtle) 1px, transparent 1px);
background-size: 20px 20px;
```

### Animated Gradient Background
```css
background: linear-gradient(
  135deg,
  var(--bg-deep) 0%,
  var(--bg-dark) 50%,
  var(--bg-deep) 100%
);
background-size: 200% 200%;
animation: gradientShift 15s ease infinite;
```

### Glow Pulse (for live indicators)
```css
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
animation: pulse 2s ease-in-out infinite;
```

## 🎯 Usage Guidelines

### When to use Primary (Cyan)
- Main action buttons
- Active states
- Links
- Focus rings
- Important indicators

### When to use Accent (Violet)
- Secondary actions
- Highlights
- Special badges
- Assistant-related items

### When to use Glass Cards
- Module containers
- Message bubbles
- Status cards
- Modals

### When to use Animations
- Page transitions
- New content appearing
- User interactions
- Loading states
- **NOT** for decorative loops (respect prefers-reduced-motion)

## 📝 Code Organization

### CSS Structure
```
1. CSS Variables (Design Tokens)
2. Reset & Base Styles
3. Layout (Grid, Flexbox)
4. Components (Buttons, Inputs, Cards)
5. Modules (Chat, Tasks, Memory, etc.)
6. Animations
7. Responsive Overrides
```

### Naming Convention
- Use BEM-like naming: `.module-element--modifier`
- Prefix utilities: `.u-text-center`, `.u-mt-4`
- Prefix states: `.is-active`, `.is-loading`

## 🚀 Performance

### Optimization Rules
1. Use `transform` and `opacity` for animations (GPU accelerated)
2. Avoid animating `width`, `height`, `top`, `left`
3. Use `will-change` sparingly
4. Debounce scroll/resize handlers
5. Lazy load images
6. Minimize repaints

### Accessibility
1. Respect `prefers-reduced-motion`
2. Maintain 4.5:1 contrast ratio
3. Focus visible on all interactive elements
4. Semantic HTML
5. ARIA labels where needed

---

This design system ensures consistency, maintainability, and a professional futuristic aesthetic across the entire VECTOR Command Center interface.
