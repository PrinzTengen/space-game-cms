Square glyph button with 1px border — for "→" next-links and "+/−" accordion toggles.

```jsx
<IconButton label="Nächster Beitrag" size={52}>→</IconButton>
<IconButton as="span" aria-hidden>+</IconButton>
```

- Glyphen nur Unicode (→ ← ↓ + − ✓).
- Innerhalb eines klickbaren Elternteils `as="span"` verwenden.
