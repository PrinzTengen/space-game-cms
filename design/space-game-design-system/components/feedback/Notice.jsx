import React from 'react';

const T = {
  success: { c: 'var(--sg-good)', line: 'var(--sg-good-line)', glow: 'rgba(80,248,131,.6)', glyph: '✓' },
  warn: { c: 'var(--sg-warn)', line: 'rgba(255,171,38,.35)', glow: 'rgba(255,171,38,.5)', glyph: '!' },
  danger: { c: 'var(--sg-danger)', line: 'rgba(252,54,36,.4)', glow: 'rgba(252,54,36,.5)', glyph: '!' }
};

export function Notice({ tone = 'success', title, children, action }) {
  const t = T[tone] || T.success;
  return (
    <div role="status" style={{ position: 'relative', overflow: 'hidden', borderRadius: 0, border: '1px solid ' + t.line, background: 'linear-gradient(180deg,#121B2A,#0A0F1D)', padding: '18px 20px', display: 'flex', flexDirection: 'column', gap: 10, color: 'var(--sg-title)' }}>
      <p style={{ margin: 0, display: 'flex', alignItems: 'center', gap: 10, fontWeight: 700, fontSize: 18, color: t.c }}>
        <span aria-hidden="true" style={{ width: 22, height: 22, borderRadius: '50%', background: 'radial-gradient(circle at 35% 35%,#FFFFFF,' + t.c + ' 60%)', boxShadow: '0 0 12px 2px ' + t.glow, color: 'var(--sg-bg)', display: 'grid', placeItems: 'center', fontSize: 12, fontWeight: 700 }}>{t.glyph}</span>{title}
      </p>
      {children && <div style={{ fontSize: 16, lineHeight: 1.5 }}>{children}</div>}
      {action}
    </div>
  );
}
