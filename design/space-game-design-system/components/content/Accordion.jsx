import React from 'react';
import { IconButton } from '../actions/IconButton.jsx';

export function AccordionItem({ id, question, answer, open = false, onToggle }) {
  const [hover, setHover] = React.useState(false);
  return (
    <div onMouseEnter={() => setHover(true)} onMouseLeave={() => setHover(false)}
      style={{ borderRadius: 0, overflow: 'hidden', border: '1px solid ' + (hover ? 'var(--sg-border-lift)' : 'var(--sg-border-soft)'), background: 'var(--sg-panel)', transition: 'border-color .15s' }}>
      <h3 style={{ margin: 0 }}>
        <button id={id + '-b'} onClick={onToggle} aria-expanded={open} aria-controls={id}
          style={{ width: '100%', minHeight: 60, padding: '8px 8px 8px 22px', border: 0, background: 'transparent', color: 'var(--sg-title)', textAlign: 'left', display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 16, fontWeight: 500, fontSize: 16, lineHeight: 1.4 }}>
          <span>{question}</span><IconButton as="span" aria-hidden="true">{open ? '−' : '+'}</IconButton>
        </button>
      </h3>
      {open && <div id={id} role="region" aria-labelledby={id + '-b'} style={{ padding: '0 70px 22px 22px', fontSize: 15, lineHeight: 1.65, color: 'var(--sg-text)' }}>{answer}</div>}
    </div>
  );
}

export function Accordion({ items = [], idPrefix = 'faq', defaultOpen = 0 }) {
  const [open, setOpen] = React.useState(defaultOpen);
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
      {items.map((it, i) => <AccordionItem key={i} id={idPrefix + '-' + i} question={it.q} answer={it.a} open={open === i} onToggle={() => setOpen(open === i ? -1 : i)} />)}
    </div>
  );
}
