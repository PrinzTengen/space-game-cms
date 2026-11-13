window.Home = function Home({ v }) {
  const { Button, Eyebrow, SectionHeader, FeatureCard, PostCard, ImagePanel } = DS;
  const sh = { textShadow: '0 1px 12px rgba(0,0,0,.6)' };
  return (
    <main>
      <section aria-labelledby="h-hero" style={{ position: 'relative', overflow: 'hidden', minHeight: '100svh', marginTop: -64, display: 'flex', flexDirection: 'column', justifyContent: 'flex-end' }}>
        <div style={{ position: 'absolute', inset: 0, background: 'var(--sg-media) url(../../assets/hero-keyart.png) center / cover no-repeat' }} />
        <div aria-hidden="true" style={{ position: 'absolute', inset: 0, background: 'var(--sg-scrim-hero)' }} />
        <div aria-hidden="true" style={{ position: 'absolute', left: '50%', top: '100%', width: 'max(220vw,1800px)', aspectRatio: '1', borderRadius: '50%', background: 'radial-gradient(circle at 50% 0,#1E2B4A 0,#040a0e 9%,#05080F 30%)', boxShadow: 'var(--sg-limb-glow)', transform: 'translateX(-50%) translateY(-6vw)', animation: 'sg-limb 1.6s var(--sg-ease) both', pointerEvents: 'none' }} />
        <div style={{ position: 'relative', width: '100%', maxWidth: 1240, margin: '0 auto', padding: '128px clamp(20px,4vw,40px) clamp(120px,15vw,200px)' }}>
          <div style={{ maxWidth: 680, display: 'flex', flexDirection: 'column', gap: 26 }}>
            <Eyebrow style={sh}>{v.t.home.kicker}</Eyebrow>
            <h1 id="h-hero" style={{ margin: 0, fontWeight: 700, fontSize: 'var(--sg-fs-display)', lineHeight: 1.08, letterSpacing: '-.01em', textShadow: 'var(--sg-text-shadow)' }}>{v.t.home.h1}</h1>
            <p style={{ margin: 0, maxWidth: '46ch', fontSize: 'var(--sg-fs-lead)', lineHeight: 1.6, ...sh }}>{v.t.home.lead}</p>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 10, alignItems: 'center' }}>
              <Button variant="galaxy" trailing="→" onClick={v.goDownload}>{v.t.home.cta}</Button>
              <Button size="lg" onClick={v.goDevlogs} style={{ minHeight: 54, padding: '0 24px', fontWeight: 600, fontSize: 16 }}>{v.t.home.cta2}</Button>
            </div>
            <p style={{ margin: 0, fontSize: 14, ...sh }}>{v.t.home.note}</p>
          </div>
        </div>
      </section>

      <section style={{ maxWidth: 1240, margin: '0 auto', padding: 'clamp(40px,6vw,80px) clamp(20px,4vw,40px) clamp(40px,5vw,64px)' }}>
        <SectionHeader eyebrow={v.t.home.pillarsLabel} title={v.t.home.pillarsTitle} />
        <ol style={{ listStyle: 'none', margin: 0, padding: 0, display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(min(100%,250px),1fr))', gap: 18 }}>
          {v.pillars.map((p, i) => <FeatureCard key={i} title={p.title} text={p.text} />)}
        </ol>
      </section>

      <section style={{ maxWidth: 1240, margin: '0 auto', padding: 'var(--sg-section-y) var(--sg-gutter)' }}>
        <SectionHeader eyebrow={v.t.home.latestLabel} title={v.t.home.latestTitle} action={<Button trailing="→" onClick={v.goBlog}>{v.t.home.all}</Button>} />
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(min(100%,300px),1fr))', gap: 18 }}>
          {v.latest.map(p => <PostCard key={p.id} title={p.title} excerpt={p.excerpt} typeLabel={p.typeLabel} date={p.date} iso={p.iso} placeholder={v.t.blog.slot} onOpen={p.open} />)}
        </div>
      </section>

      <section style={{ maxWidth: 1240, margin: '0 auto', padding: 'var(--sg-section-y) var(--sg-gutter) clamp(72px,9vw,120px)' }}>
        <ImagePanel src="../../assets/cta-station.png">
          <h2 style={{ margin: 0, fontWeight: 700, fontSize: 'clamp(28px,3.6vw,46px)', lineHeight: 1.12, letterSpacing: '-.01em' }}>{v.t.home.ctaTitle}</h2>
          <p style={{ margin: 0, maxWidth: '48ch', fontSize: 18, lineHeight: 1.55, textShadow: '0 1px 14px rgba(0,0,0,.8)' }}>{v.t.home.ctaText}</p>
          <Button size="lg" caps trailing="→" onClick={v.goDownload} style={{ marginTop: 8 }}>{v.t.home.ctaBtn}</Button>
        </ImagePanel>
      </section>
    </main>
  );
};
