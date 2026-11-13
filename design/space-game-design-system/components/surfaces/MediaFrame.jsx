import React from 'react';

export function MediaFrame({ src, alt = '', ratio = '16/10', bordered = false, placeholder, children, style, ...rest }) {
  return (
    <div style={{ position: 'relative', aspectRatio: ratio, overflow: 'hidden', borderRadius: 0, background: 'var(--sg-media)',
      border: bordered ? '1px solid var(--sg-border-soft)' : 0, ...style }} {...rest}>
      {src ? <img src={src} alt={alt} style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', objectFit: 'cover' }} />
        : <span style={{ position: 'absolute', inset: 0, display: 'grid', placeItems: 'center', fontSize: 11, letterSpacing: '.12em', textTransform: 'uppercase', color: 'var(--sg-dim)' }}>{placeholder}</span>}
      {children}
      <span aria-hidden="true" style={{ position: 'absolute', inset: 0, pointerEvents: 'none', boxShadow: 'var(--sg-media-vignette)' }} />
    </div>
  );
}
