import React from 'react';

const S = {
  done: { bg: 'var(--sg-button)', fg: 'var(--sg-good)', orb: 'var(--sg-good)' },
  current: { bg: 'var(--sg-hover)', fg: 'var(--sg-accent-hover)', orb: 'var(--sg-accent)' },
  pending: { bg: 'transparent', fg: 'var(--sg-text)', orb: 'var(--sg-border)' }
};

export function Stepper({ steps = [] }) {
  return (
    <ol style={{ listStyle: 'none', margin: 0, padding: 5, display: 'flex', flexWrap: 'wrap', gap: 4, borderRadius: 0, border: '1px solid var(--sg-border-soft)', background: 'var(--sg-panel)' }}>
      {steps.map((st, i) => {
        const s = S[st.state] || S.pending;
        return (
          <li key={i} aria-current={st.state === 'current' ? 'step' : undefined} style={{ flex: '1 1 200px', display: 'flex', alignItems: 'center', gap: 12, minHeight: 46, padding: '4px 18px 4px 8px', background: s.bg }}>
            <span aria-hidden="true" style={{ width: 22, height: 22, flex: 'none', display: 'grid', placeItems: 'center', border: '1px solid ' + s.orb, color: s.orb, fontSize: 12, fontWeight: 700, lineHeight: 1 }}>{st.state === 'done' ? '✓' : ''}</span>
            <span style={{ display: 'flex', flexDirection: 'column', gap: 1, minWidth: 0 }}>
              <span style={{ fontWeight: 600, fontSize: 14, lineHeight: 1.3, color: 'var(--sg-title)' }}>{st.label}</span>
              <span style={{ fontSize: 11, color: s.fg }}>{st.status}</span>
            </span>
          </li>
        );
      })}
    </ol>
  );
}
