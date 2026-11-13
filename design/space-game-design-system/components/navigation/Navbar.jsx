import React from 'react';
import { Brand } from './Brand.jsx';

function NavItem({ item }) {
  const [hover, setHover] = React.useState(false);
  return (
    <li>
      <button onClick={item.onClick} aria-current={item.active ? 'page' : undefined}
        onMouseEnter={() => setHover(true)} onMouseLeave={() => setHover(false)}
        style={{ minHeight: 44, padding: '0 10px', border: 0, background: 'transparent', boxShadow: item.active ? 'inset 0 -2px 0 var(--sg-accent)' : 'none',
          color: item.active || hover ? 'var(--sg-title)' : 'var(--sg-text)', fontFamily: 'var(--sg-font)', fontSize: 11, letterSpacing: '.12em',
          textTransform: 'uppercase', whiteSpace: 'nowrap', transition: 'color .15s' }}>{item.label}</button>
    </li>
  );
}

export function Navbar({ items = [], badge, onHome, navLabel = 'Hauptnavigation', right, sticky = true }) {
  return (
    <header style={{ position: sticky ? 'sticky' : 'relative', top: 0, zIndex: 20, background: 'var(--sg-nav-glass)', backdropFilter: 'blur(12px)', WebkitBackdropFilter: 'blur(12px)', borderBottom: '1px solid var(--sg-border-soft)' }}>
      <div style={{ minHeight: 64, padding: '8px clamp(16px,2.5vw,36px)', display: 'flex', alignItems: 'center', gap: '8px 18px', flexWrap: 'wrap' }}>
        <Brand badge={badge} onClick={onHome} />
        <nav aria-label={navLabel}>
          <ul style={{ listStyle: 'none', margin: 0, padding: 0, display: 'flex', flexWrap: 'wrap', gap: 2 }}>
            {items.map((it, i) => <NavItem key={i} item={it} />)}
          </ul>
        </nav>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginLeft: 'auto' }}>{right}</div>
      </div>
    </header>
  );
}
