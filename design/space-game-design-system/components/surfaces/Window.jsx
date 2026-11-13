import React from 'react';

const PADS = { none: 0, sm: 8, md: 'clamp(22px,3vw,32px)', lg: 'clamp(24px,3.5vw,44px)', card: '28px 26px 30px' };

export function Window({ as = 'div', solid = false, interactive = false, padding = 'md', children, style, ...rest }) {
  const [hover, setHover] = React.useState(false);
  const Tag = as;
  const lift = interactive && hover;
  return (
    <Tag onMouseEnter={interactive ? () => setHover(true) : undefined} onMouseLeave={interactive ? () => setHover(false) : undefined}
      style={{ position: 'relative', overflow: 'hidden', borderRadius: 0, boxShadow: 'none',
        border: '1px solid ' + (lift ? 'var(--sg-border-lift)' : 'var(--sg-border-soft)'),
        background: 'var(--sg-window-corners), var(--sg-scanlines), ' + (solid ? 'var(--sg-panel)' : 'var(--sg-glass)'),
        padding: PADS[padding] ?? padding, transform: lift ? 'translateY(-3px)' : 'none',
        transition: interactive ? 'transform .25s, border-color .25s' : undefined, cursor: interactive ? 'pointer' : undefined, ...style }} {...rest}>
      {children}
    </Tag>
  );
}
