import React from 'react';

export function ImagePanel({ src, position = 'center 55%', align = 'center', children, style, ...rest }) {
  return (
    <div style={{ position: 'relative', overflow: 'hidden', borderRadius: 0, border: '1px solid var(--sg-border-soft)',
      background: 'var(--sg-scrim-panel), url(' + JSON.stringify(src) + ') ' + position + ' / cover no-repeat, #0A0F1D',
      padding: 'clamp(72px,10vw,140px) clamp(24px,5vw,72px)', display: 'flex', flexDirection: 'column',
      alignItems: align === 'center' ? 'center' : 'flex-start', textAlign: align, gap: 16, textShadow: '0 2px 24px rgba(0,0,0,.7)', ...style }} {...rest}>
      {children}
    </div>
  );
}
