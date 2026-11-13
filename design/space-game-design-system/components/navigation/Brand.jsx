import React from 'react';

export function Brand({ badge, onClick, label = 'Space Game' }) {
  const Tag = onClick ? 'button' : 'span';
  return (
    <Tag onClick={onClick} aria-label={onClick ? label + ' – Start' : undefined}
      style={{ display: 'flex', alignItems: 'center', gap: 10, minHeight: 44, padding: 0, border: 0, background: 'none', color: 'var(--sg-title)', fontFamily: 'var(--sg-font)' }}>
      <span aria-hidden="true" style={{ width: 28, height: 28, borderRadius: '50%', flex: 'none', background: 'radial-gradient(circle at 35% 30%,#FFE0B0 0,#E39B36 30%,#5A3A14 62%,#0B1020 64%)', boxShadow: '0 0 14px rgba(227,155,54,.55)' }} />
      <span style={{ fontWeight: 700, fontSize: 17, letterSpacing: '.02em', whiteSpace: 'nowrap' }}>{label}</span>
      {badge && <span style={{ fontSize: 10, letterSpacing: '.14em', textTransform: 'uppercase', color: 'var(--sg-accent)', border: '1px solid var(--sg-accent-line)', padding: '3px 7px 2px', whiteSpace: 'nowrap' }}>{badge}</span>}
    </Tag>
  );
}
