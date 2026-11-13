import React from 'react';
import { Eyebrow } from './Eyebrow.jsx';

const SIZES = { page: 'clamp(40px,5.4vw,72px)', section: 'clamp(28px,3.2vw,42px)' };

export function SectionHeader({ eyebrow, title, lead, level = 'section', as, action, id }) {
  const H = as || (level === 'page' ? 'h1' : 'h2');
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'end', gap: 20, flexWrap: 'wrap', marginBottom: 28 }}>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
        {eyebrow && <Eyebrow>{eyebrow}</Eyebrow>}
        <H id={id} style={{ margin: 0, fontFamily: 'var(--sg-font)', fontWeight: 700, fontSize: SIZES[level], lineHeight: level === 'page' ? 1.05 : 1.12, letterSpacing: '-.01em', color: 'var(--sg-title)' }}>{title}</H>
        {lead && <p style={{ margin: 0, maxWidth: '52ch', fontSize: 18, lineHeight: 1.55, color: 'var(--sg-text)' }}>{lead}</p>}
      </div>
      {action}
    </div>
  );
}
