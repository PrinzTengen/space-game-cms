import React from 'react';

export function Eyebrow({ tone = 'dim', size = 12, as = 'p', children, style, ...rest }) {
  const Tag = as;
  return <Tag style={{ margin: 0, fontFamily: 'var(--sg-font)', fontSize: size, letterSpacing: '.12em', textTransform: 'uppercase', color: tone === 'accent' ? 'var(--sg-accent)' : 'var(--sg-dim)', ...style }} {...rest}>{children}</Tag>;
}
