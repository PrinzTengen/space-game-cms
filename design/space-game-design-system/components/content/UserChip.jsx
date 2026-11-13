import React from 'react';

export function Avatar({ initials, size = 32 }) {
  return <span aria-hidden="true" style={{ width: size, height: size, flex: 'none', borderRadius: 0, background: 'var(--sg-hover)', boxShadow: 'inset 0 1px 0 rgba(255,255,255,.18), 0 0 0 1px var(--sg-accent-line)', color: 'var(--sg-accent)', display: 'grid', placeItems: 'center', fontFamily: 'var(--sg-font)', fontSize: size > 40 ? 13 : 11, fontWeight: 500 }}>{initials}</span>;
}

export function UserChip({ initials, handle, onClick }) {
  const [hover, setHover] = React.useState(false);
  return (
    <button onClick={onClick} onMouseEnter={() => setHover(true)} onMouseLeave={() => setHover(false)}
      style={{ display: 'flex', alignItems: 'center', gap: 10, minHeight: 44, padding: '0 16px 0 5px', borderRadius: 0, border: '1px solid ' + (hover ? 'var(--sg-accent)' : 'var(--sg-border-soft)'), background: hover ? 'var(--sg-hover)' : 'var(--sg-button)', color: hover ? 'var(--sg-accent-hover)' : 'var(--sg-accent)', fontSize: 14, fontWeight: 500, whiteSpace: 'nowrap' }}>
      <Avatar initials={initials} />{handle}
    </button>
  );
}
