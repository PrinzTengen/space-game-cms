import React from 'react';
import { Window } from '../surfaces/Window.jsx';

export function FeatureCard({ title, text, as = 'li' }) {
  return (
    <Window as={as} padding="card" style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
      <h3 style={{ margin: 0, fontWeight: 700, fontSize: 25, lineHeight: 1.15, letterSpacing: '-.01em', color: 'var(--sg-title)' }}>{title}</h3>
      <p style={{ margin: 0, fontSize: 16, lineHeight: 1.6, color: 'var(--sg-text)', maxWidth: '36ch' }}>{text}</p>
    </Window>
  );
}
