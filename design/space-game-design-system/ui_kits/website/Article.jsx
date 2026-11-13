window.Article = function Article({ v }) {
  const { Button, Window, Tag, MediaFrame, IconButton } = DS;
  const a = v.article, n = v.next;
  return (
    <PageWrap style={{ paddingTop: 'clamp(32px,5vw,64px)' }}>
      <Button size="sm" leading="←" onClick={v.goBlog} style={{ minHeight: 44, marginBottom: 20 }}>{v.t.art.back}</Button>
      <Window as="article" padding="clamp(24px,4vw,56px)">
        <header style={{ maxWidth: 860, margin: '0 auto', display: 'flex', flexDirection: 'column', gap: 20, textAlign: 'center', alignItems: 'center' }}>
          <span style={{ display: 'flex', gap: 10, alignItems: 'center', flexWrap: 'wrap', justifyContent: 'center', fontSize: 12, color: 'var(--sg-dim)' }}><Tag size="md">{a.typeLabel}</Tag><time dateTime={a.iso}>{a.date}</time><span>· {a.read}</span></span>
          <h1 style={{ margin: 0, fontWeight: 700, fontSize: 'var(--sg-fs-article-title)', lineHeight: 1.1, letterSpacing: '-.01em' }}>{a.title}</h1>
          <p style={{ margin: 0, maxWidth: '58ch', fontSize: 'clamp(18px,1.5vw,21px)', lineHeight: 1.5 }}>{a.excerpt}</p>
        </header>
        <MediaFrame ratio="21/9" bordered placeholder={v.t.art.slot} style={{ margin: 'clamp(28px,4vw,48px) auto' }} />
        <div style={{ maxWidth: '66ch', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: 22 }}>
          {a.blocks.map((b, i) => b.isH
            ? <h2 key={i} style={{ margin: '20px 0 0', fontWeight: 700, fontSize: 26, lineHeight: 1.2, letterSpacing: '-.01em' }}>{b.text}</h2>
            : b.isImg ? <figure key={i} style={{ margin: '12px 0', display: 'flex', flexDirection: 'column', gap: 10 }}><MediaFrame ratio="16/9" bordered placeholder={v.t.art.slot} /><figcaption style={{ fontSize: 12, color: 'var(--sg-dim)' }}>{b.text}</figcaption></figure>
            : <p key={i} style={{ margin: 0, fontSize: 19, lineHeight: 1.7 }}>{b.text}</p>)}
        </div>
      </Window>
      <nav aria-label={v.t.art.next} style={{ marginTop: 18 }}>
        <button onClick={n.open} style={{ width: '100%', textAlign: 'left', borderRadius: 0, border: '1px solid var(--sg-border-soft)', background: 'var(--sg-panel)', padding: '10px 10px 10px 26px', color: 'var(--sg-title)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 20 }}>
          <span style={{ display: 'flex', flexDirection: 'column', gap: 4, padding: '8px 0' }}>
            <span style={{ fontSize: 12, color: 'var(--sg-dim)' }}>{v.t.art.next} · {n.typeLabel}</span>
            <span style={{ fontWeight: 700, fontSize: 'clamp(17px,2vw,21px)', lineHeight: 1.3 }}>{n.title}</span>
          </span>
          <IconButton as="span" size={52} aria-hidden="true">→</IconButton>
        </button>
      </nav>
    </PageWrap>
  );
};
