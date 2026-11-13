import React from 'react';

const R = (a, b) => Math.floor(Math.random() * (b - a + 1) + a);
const SPARK = 'var(--sg-accent-hover)';
const abs = { position: 'absolute', pointerEvents: 'none' };

function GalaxyFx({ hover }) {
  const set = React.useMemo(() => ({
    dots: Array.from({ length: 12 }, () => ({ x: R(3, 97), y: R(12, 88), dur: R(3, 7), del: R(0, 6), s: [1.5, 2, 2, 2.5, 3, 3.5][R(0, 5)], a: R(50, 100) / 100 })),
    orbit: Array.from({ length: 24 }, () => ({ d: R(30, 170), dur: R(6, 20), del: R(1, 10), a: R(60, 100) / 100, s: R(2, 4) }))
  }), []);
  const L = 1.5, B = 9, c = 'var(--sg-accent)';
  return (
    <>
      <span aria-hidden="true" style={{ ...abs, inset: 0, zIndex: 0, opacity: hover ? 1 : .85, transition: 'opacity .3s' }}>
        {set.dots.map((d, i) => <span key={i} style={{ position: 'absolute', left: d.x + '%', top: d.y + '%', width: d.s, height: d.s, borderRadius: '50%', background: SPARK, boxShadow: d.s > 2.5 ? '0 0 6px 1px ' + SPARK : 'none', opacity: d.a, animation: 'sg-twinkle ' + d.dur + 's ' + (-d.del) + 's ease-in-out infinite' }} />)}
      </span>
      <span aria-hidden="true" style={{ ...abs, zIndex: 0, width: '100%', aspectRatio: '1', top: '50%', left: '50%', translate: '-50% -50%', overflow: 'hidden', opacity: hover ? .8 : 0, transition: 'opacity .3s' }}>
        <span style={{ position: 'absolute', width: '200%', height: '200%', top: '50%', left: '50%', borderRadius: '50%', transform: 'translate(-28%,-40%) rotateX(-24deg) rotateY(-30deg) rotateX(90deg)', transformStyle: 'preserve-3d' }}>
          {set.orbit.map((o, i) => <span key={i} style={{ position: 'absolute', '--d': o.d + 'px', top: '50%', left: '50%', width: o.s, height: o.s, borderRadius: '50%', background: SPARK, boxShadow: '0 0 4px ' + SPARK, opacity: o.a, transform: 'translate(-50%,-50%) rotate(10deg) rotate(0deg) translateY(' + o.d + 'px)', animation: 'sg-orbit ' + o.dur + 's ' + (-o.del) + 's infinite linear' }} />)}
        </span>
      </span>
      <span aria-hidden="true" style={{ ...abs, inset: 4, zIndex: 1, opacity: hover ? 1 : .7, transition: 'opacity .25s' }}>
        <span style={{ position: 'absolute', left: -4, top: -4, width: 20, height: L, background: c, transform: 'translate(-2px,7.25px) rotate(-45deg)' }} />
        <span style={{ position: 'absolute', right: 0, top: 0, width: B, height: B, borderRight: L + 'px solid ' + c, borderTop: L + 'px solid ' + c }} />
        <span style={{ position: 'absolute', left: 0, bottom: 0, width: B, height: B, borderLeft: L + 'px solid ' + c, borderBottom: L + 'px solid ' + c }} />
        <span style={{ position: 'absolute', right: -4, bottom: -4, width: 20, height: L, background: c, transform: 'translate(2px,-7.25px) rotate(-45deg)' }} />
      </span>
    </>
  );
}

const SIZES = { sm: { minHeight: 40, padding: '0 16px', fontSize: 14 }, md: { minHeight: 46, padding: '0 20px', fontSize: 15 }, lg: { minHeight: 56, padding: '0 30px', fontSize: 16 } };

export function Button({ variant = 'secondary', size = 'md', caps = false, trailing, leading, fullWidth = false, disabled = false, loading = false, type = 'button', onClick, children, style, ...rest }) {
  const [hover, setHover] = React.useState(false);
  const [down, setDown] = React.useState(false);
  const galaxy = variant === 'galaxy';
  const sz = SIZES[size] || SIZES.md;
  const base = {
    position: 'relative', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', gap: 10,
    width: fullWidth ? '100%' : undefined, borderRadius: 0, fontFamily: 'var(--sg-font)', whiteSpace: 'nowrap',
    cursor: disabled ? 'not-allowed' : 'pointer', transform: down && !disabled ? 'translateY(1px)' : 'none',
    transition: 'background .3s, box-shadow .3s, color .3s, border-color .15s'
  };
  let look;
  if (galaxy) {
    const small = size === 'sm';
    const ch = small ? 10 : 14;
    look = {
      minHeight: small ? 44 : 56, padding: small ? '0 20px' : '0 30px', border: 0, overflow: 'hidden', isolation: 'isolate',
      clipPath: 'polygon(' + ch + 'px 0,100% 0,100% calc(100% - ' + ch + 'px),calc(100% - ' + ch + 'px) 100%,0 100%,0 ' + ch + 'px)',
      fontWeight: 700, fontSize: small ? 12 : 13, letterSpacing: '.14em', textTransform: 'uppercase',
      color: hover ? '#fff' : 'var(--sg-title)', transformStyle: 'preserve-3d', perspective: '100vmin',
      background: hover ? 'var(--sg-galaxy-bg-hover)' : 'var(--sg-galaxy-bg)',
      boxShadow: hover ? 'var(--sg-glow)' : 'var(--sg-shadow)', opacity: disabled ? .5 : 1
    };
  } else {
    look = {
      ...sz, ...(caps ? { fontWeight: 600, fontSize: 13, letterSpacing: '.14em', textTransform: 'uppercase' } : { fontWeight: 500 }),
      border: '1px solid ' + (hover && !disabled ? 'var(--sg-accent)' : 'var(--sg-border-soft)'),
      background: disabled ? 'var(--sg-panel)' : down ? 'var(--sg-pressed)' : hover ? 'var(--sg-hover)' : 'var(--sg-button)',
      color: disabled ? 'var(--sg-text)' : hover ? 'var(--sg-accent-hover)' : 'var(--sg-accent)',
      boxShadow: caps ? 'var(--sg-shadow)' : 'none'
    };
  }
  const z = { position: 'relative', zIndex: 2 };
  return (
    <button type={type} disabled={disabled || loading} aria-busy={loading || undefined} onClick={onClick}
      onMouseEnter={() => setHover(true)} onMouseLeave={() => { setHover(false); setDown(false); }}
      onFocus={() => setHover(true)} onBlur={() => setHover(false)}
      onMouseDown={() => setDown(true)} onMouseUp={() => setDown(false)}
      style={{ ...base, ...look, ...style }} {...rest}>
      {galaxy && !disabled && <GalaxyFx hover={hover} />}
      {loading && <span aria-hidden="true" style={{ ...z, width: 14, height: 14, border: '2px solid rgba(255,255,255,.2)', borderTopColor: 'var(--sg-accent)', animation: 'sg-spin .8s linear infinite' }} />}
      {leading && <span aria-hidden="true" style={{ ...z, color: 'var(--sg-accent)' }}>{leading}</span>}
      <span style={z}>{children}</span>
      {trailing && <span aria-hidden="true" style={{ ...z, color: 'var(--sg-accent)' }}>{trailing}</span>}
    </button>
  );
}
