import React from 'react';

export function RadioCard({ label, sub, checked = false, onSelect }) {
  const [hover, setHover] = React.useState(false);
  return (
    <button role="radio" aria-checked={checked} onClick={onSelect} onMouseEnter={() => setHover(true)} onMouseLeave={() => setHover(false)}
      style={{ minHeight: 76, padding: '14px 18px 14px 16px', borderRadius: 0, textAlign: 'left', width: '100%',
        background: checked ? 'var(--sg-hover)' : 'rgba(0,0,0,.25)', border: '1px solid var(--sg-border-soft)',
        boxShadow: checked ? 'inset 0 1px 0 rgba(255,255,255,.4), inset 0 -1px 0 rgba(0,0,0,.6), 0 4px 10px rgba(0,0,0,.35)' : 'inset 0 2px 6px rgba(0,0,0,.45)',
        color: checked || hover ? 'var(--sg-title)' : 'var(--sg-text)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 12, transition: 'color .15s' }}>
      <span style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
        <span style={{ fontWeight: 600, fontSize: 18 }}>{label}</span>
        {sub && <span style={{ fontSize: 11, color: 'var(--sg-dim)' }}>{sub}</span>}
      </span>
      <span aria-hidden="true" style={{ width: 30, height: 30, flex: 'none', borderRadius: 0, border: '1px solid var(--sg-border-soft)', background: 'var(--sg-button)', display: 'grid', placeItems: 'center' }}>
        {checked && <span style={{ width: 10, height: 10, borderRadius: '50%', background: 'radial-gradient(circle at 35% 35%,#FFFFFF,var(--sg-accent) 60%)', boxShadow: '0 0 10px 2px rgba(139,224,236,.7)' }} />}
      </span>
    </button>
  );
}

export function RadioCardGroup({ label, options = [], value, onChange }) {
  return (
    <div role="radiogroup" aria-label={label} style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(min(100%,190px),1fr))', gap: 10 }}>
      {options.map(o => <RadioCard key={o.value} label={o.label} sub={o.sub} checked={o.value === value} onSelect={() => onChange && onChange(o.value)} />)}
    </div>
  );
}
