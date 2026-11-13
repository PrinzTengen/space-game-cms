import React from 'react';
import { Window } from '../surfaces/Window.jsx';
import { MediaFrame } from '../surfaces/MediaFrame.jsx';
import { Tag } from './Tag.jsx';

export function PostCard({ title, excerpt, typeLabel, date, iso, read, image, placeholder = 'Bild', more, onOpen, headingLevel = 'h3' }) {
  const H = headingLevel;
  return (
    <Window as="article" interactive padding="sm" onClick={onOpen} style={{ display: 'flex', flexDirection: 'column' }}>
      <MediaFrame src={image} placeholder={placeholder} />
      <div style={{ padding: '18px 14px 14px', display: 'flex', flexDirection: 'column', gap: 12, flex: 1 }}>
        <span style={{ display: 'flex', gap: 10, alignItems: 'center', flexWrap: 'wrap', fontSize: 11, color: 'var(--sg-dim)' }}>
          <Tag>{typeLabel}</Tag><time dateTime={iso}>{date}</time>{read && <span>· {read}</span>}
        </span>
        <H style={{ margin: 0, fontWeight: 700, fontSize: 20, lineHeight: 1.3, letterSpacing: '-.01em', color: 'var(--sg-title)' }}>{title}</H>
        <p style={{ margin: 0, fontSize: 15, lineHeight: 1.55, color: 'var(--sg-text)' }}>{excerpt}</p>
        {more && <span aria-hidden="true" style={{ marginTop: 'auto', alignSelf: 'flex-start', display: 'inline-flex', alignItems: 'center', gap: 8, minHeight: 36, padding: '0 14px', border: '1px solid var(--sg-border-soft)', background: 'var(--sg-button)', fontWeight: 500, fontSize: 13, color: 'var(--sg-accent)' }}>{more} →</span>}
      </div>
    </Window>
  );
}
