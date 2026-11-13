import React from 'react';

function Opt({ o, on, size, bare, onChange }) {
  const [hover, setHover] = React.useState(false);
  const sm = size === 'sm';
  return (
    <button type="button" aria-pressed={on} onClick={() => onChange && onChange(o.value)} lang={o.lang}
      onMouseEnter={() => setHover(true)} onMouseLeave={() => setHover(false)}
      style={{ minHeight: 40, minWidth: bare ? 44 : undefined, padding: bare ? '0 10px' : sm ? '0 12px' : '0 16px', border: 0, borderRadius: 0,
        background: on ? 'var(--sg-hover)' : bare ? 'var(--sg-button)' : 'transparent',
        boxShadow: on && !bare ? 'inset 0 1px 0 rgba(255,255,255,.4), inset 0 -1px 0 rgba(0,0,0,.6), 0 4px 10px rgba(0,0,0,.35)' : 'none',
        color: on ? (bare ? 'var(--sg-accent)' : 'var(--sg-title)') : hover ? 'var(--sg-title)' : bare ? 'var(--sg-dim)' : 'var(--sg-text)',
        fontFamily: 'var(--sg-font)', fontWeight: 500, fontSize: sm ? 12 : 14, whiteSpace: 'nowrap', display: 'flex', alignItems: 'center', gap: 8, transition: 'color .15s' }}>
      {o.label}{o.count != null && <span style={{ fontSize: 11, opacity: .75 }}>{o.count}</span>}
    </button>
  );
}

export function Segment({ options = [], value, onChange, size = 'md', bare = false, label }) {
  return (
    <div role="group" aria-label={label} style={bare ? { display: 'flex', gap: 4 } : { display: 'inline-flex', flexWrap: 'nowrap', gap: 4, padding: 5, borderRadius: 0, border: '1px solid var(--sg-border-soft)', background: 'var(--sg-panel)' }}>
      {options.map(o => <Opt key={o.value} o={o} on={o.value === value} size={size} bare={bare} onChange={onChange} />)}
    </div>
  );
}
