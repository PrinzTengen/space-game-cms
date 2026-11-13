import React from 'react';

const T = { good: ['var(--sg-good)', 'var(--sg-glow-good)'], warn: ['var(--sg-warn)', 'none'], danger: ['var(--sg-danger)', 'none'], accent: ['var(--sg-accent)', '0 0 8px 1px rgba(139,224,236,.55)'], muted: ['var(--sg-dim)', 'none'] };

export function StatusDot({ tone = 'muted', size = 7, label }) {
  const t = T[tone] || T.muted;
  return <span role={label ? 'img' : undefined} aria-label={label} aria-hidden={label ? undefined : 'true'} style={{ display: 'inline-block', width: size, height: size, borderRadius: '50%', background: t[0], boxShadow: t[1], verticalAlign: 'middle', flex: 'none' }} />;
}
