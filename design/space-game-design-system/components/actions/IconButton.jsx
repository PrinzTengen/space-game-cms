import React from 'react';

export function IconButton({ size = 44, label, children = '→', onClick, as = 'button', style, ...rest }) {
  const [hover, setHover] = React.useState(false);
  const Tag = as;
  return (
    <Tag type={as === 'button' ? 'button' : undefined} aria-label={label} onClick={onClick}
      onMouseEnter={() => setHover(true)} onMouseLeave={() => setHover(false)}
      style={{ flex: 'none', width: size, height: size, display: 'grid', placeItems: 'center', borderRadius: 0, padding: 0,
        border: '1px solid ' + (hover ? 'var(--sg-accent)' : 'var(--sg-border-soft)'), background: hover ? 'var(--sg-hover)' : 'var(--sg-button)',
        color: hover ? 'var(--sg-accent-hover)' : 'var(--sg-accent)', fontFamily: 'var(--sg-font)', fontSize: size > 48 ? 20 : 18, fontWeight: 600,
        cursor: 'pointer', transition: 'background .3s, color .3s, border-color .15s', ...style }} {...rest}>
      <span aria-hidden="true">{children}</span>
    </Tag>
  );
}
