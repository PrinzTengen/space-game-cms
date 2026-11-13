import React from 'react';

export function Footer({ line, pagesLabel = 'Seiten', links = [], rights }) {
  return (
    <footer style={{ position: 'relative', borderTop: '1px solid var(--sg-line)' }}>
      <div aria-hidden="true" style={{ position: 'absolute', left: '50%', top: -1, transform: 'translateX(-50%)', width: 'min(60%,720px)', height: 1, background: 'linear-gradient(90deg,transparent,rgba(169,236,245,.9),transparent)', boxShadow: '0 0 18px rgba(139,224,236,.6)' }} />
      <div style={{ maxWidth: 1240, margin: '0 auto', padding: '44px clamp(20px,4vw,40px) 32px', display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(min(100%,240px),1fr))', gap: 32 }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          <span style={{ fontWeight: 700, fontSize: 17, letterSpacing: '-.01em', color: 'var(--sg-title)' }}>Space Game</span>
          <p style={{ margin: 0, maxWidth: '36ch', fontSize: 15, lineHeight: 1.55, color: 'var(--sg-text)' }}>{line}</p>
        </div>
        <nav aria-label={pagesLabel}>
          <p style={{ margin: '0 0 10px', fontSize: 11, color: 'var(--sg-dim)' }}>{pagesLabel}</p>
          <ul style={{ listStyle: 'none', margin: 0, padding: 0, display: 'flex', flexDirection: 'column', gap: 2 }}>
            {links.map((l, i) => <li key={i}><button onClick={l.onClick} style={{ minHeight: 34, padding: 0, background: 'none', border: 0, color: 'var(--sg-title)', fontSize: 15 }}
              onMouseEnter={e => e.currentTarget.style.color = 'var(--sg-accent)'} onMouseLeave={e => e.currentTarget.style.color = 'var(--sg-title)'}>{l.label}</button></li>)}
          </ul>
        </nav>
        <p style={{ margin: 0, alignSelf: 'end', fontSize: 11, color: 'var(--sg-dim)' }}>{rights}</p>
      </div>
    </footer>
  );
}
