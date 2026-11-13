import React from 'react';

export function SpecList({ items = [] }) {
  return (
    <dl style={{ margin: 0, display: 'grid', gridTemplateColumns: 'max-content minmax(0,1fr)', gap: '8px 20px', fontFamily: 'var(--sg-font)', fontSize: 12, padding: '16px 20px', borderRadius: 0, background: 'var(--sg-inset)', border: '1px solid var(--sg-border-soft)', boxShadow: 'var(--sg-inset-well)', color: 'var(--sg-title)' }}>
      {items.map(([k, v], i) => <React.Fragment key={i}><dt style={{ color: 'var(--sg-text)' }}>{k}</dt><dd style={{ margin: 0, overflowWrap: 'anywhere' }}>{v}</dd></React.Fragment>)}
    </dl>
  );
}
