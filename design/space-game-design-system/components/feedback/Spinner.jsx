import React from 'react';

export function Spinner({ size = 14 }) {
  return <span aria-hidden="true" style={{ display: 'inline-block', width: size, height: size, flex: 'none', border: '2px solid rgba(255,255,255,.2)', borderTopColor: 'var(--sg-accent)', borderRadius: 0, animation: 'sg-spin .8s linear infinite' }} />;
}
