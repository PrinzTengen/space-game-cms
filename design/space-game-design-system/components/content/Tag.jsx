import React from 'react';

const DOT = { accent: ['var(--sg-accent)', 'rgba(139,224,236,.5)'], good: ['var(--sg-good)', 'rgba(80,248,131,.5)'], muted: ['var(--sg-border)', 'transparent'] };

export function Tag({ tone = 'accent', size = 'sm', children }) {
  const d = DOT[tone] || DOT.accent;
  return (
    <span style={{ display: 'inline-flex', alignItems: 'center', gap: 7, padding: size === 'md' ? '6px 12px 6px 9px' : '5px 11px 5px 8px', borderRadius: 0,
      border: '1px solid var(--sg-border-soft)', background: 'transparent', color: 'var(--sg-title)', fontFamily: 'var(--sg-font)', fontSize: size === 'md' ? 12 : 11, whiteSpace: 'nowrap' }}>
      <span aria-hidden="true" style={{ width: 7, height: 7, borderRadius: '50%', background: d[0], boxShadow: '0 0 8px 1px ' + d[1] }} />{children}
    </span>
  );
}
