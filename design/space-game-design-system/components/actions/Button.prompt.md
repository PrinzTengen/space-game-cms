Action button — use variant="galaxy" for the single main CTA per view, "secondary" for everything else.

```jsx
<Button variant="galaxy" trailing="→">Launcher herunterladen</Button>
<Button size="lg" style={{fontSize:16,fontWeight:600}}>Devlogs lesen</Button>
<Button size="sm" caps>Anmelden</Button>
<Button loading>Verbinde mit Discord …</Button>
```

- galaxy: 56px, 14px Fase, Sterne + Orbit bei Hover, Label 13px/700/.14em Versal. Nie zwei pro Ansicht.
- secondary: 1px Rand, Fläche --sg-button, Text Akzent; Hover --sg-hover + Akzent-Rand; Pressed 1px nach unten.
- caps: Versal-Variante für Header-„Anmelden“ und CTA-Panel.
- Pfeile als Unicode-Glyph (→ ← ↓), nie Icons.
