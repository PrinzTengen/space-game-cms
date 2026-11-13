window.Download = function Download({ v }) {
  const { SectionHeader, Stepper, Window, Button, Avatar, RadioCardGroup, SpecList, Notice } = DS;
  const steps = v.steps.map(s => ({ label: s.label, status: s.status, state: s.isDone ? 'done' : s.isCurrent ? 'current' : 'pending' }));
  const os = v.osList.find(o => o.active);
  const h2 = { margin: 0, fontWeight: 700, fontSize: 'var(--sg-fs-panel-title)', lineHeight: 1.15, letterSpacing: '-.01em' };
  return (
    <PageWrap>
      <SectionHeader level="page" eyebrow={v.t.dl.label} title={v.t.dl.title} lead={v.t.dl.lead} />
      <div style={{ marginBottom: 20 }}><Stepper steps={steps} /></div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(min(100%,400px),1fr))', gap: 18, alignItems: 'start' }}>
        <Window as="section" padding="lg" style={{ display: 'flex', flexDirection: 'column', gap: 22 }}>
          <p role="status" aria-live="polite" style={{ position: 'absolute', width: 1, height: 1, overflow: 'hidden', clip: 'rect(0 0 0 0)' }}>{v.msg}</p>
          {!v.isIn ? <>
            <h2 style={h2}>{v.t.dl.loginTitle}</h2>
            <p style={{ margin: 0, fontSize: 16, lineHeight: 1.6, maxWidth: '52ch' }}>{v.t.dl.loginText}</p>
            {v.isLoading ? <Button loading style={{ alignSelf: 'flex-start', minHeight: 54 }}>{v.t.dl.connecting}</Button>
              : <Button variant="galaxy" trailing="→" onClick={v.login} style={{ alignSelf: 'flex-start' }}>{v.t.dl.loginBtn}</Button>}
            <p style={{ margin: 0, fontSize: 14 }}>{v.t.dl.privacy}</p>
          </> : <>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 12, flexWrap: 'wrap', padding: 6, border: '1px solid var(--sg-border-soft)', background: 'var(--sg-panel)', marginRight: 36 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                <Avatar initials={v.user.initials} size={44} />
                <span style={{ display: 'flex', flexDirection: 'column', gap: 2 }}><span style={{ fontSize: 11, color: 'var(--sg-dim)' }}>{v.t.dl.signedIn}</span><span style={{ fontWeight: 600, fontSize: 15, color: 'var(--sg-title)' }}>{v.user.name} <span style={{ fontWeight: 400, color: 'var(--sg-text)' }}>{v.user.handle}</span></span></span>
              </div>
              <Button size="sm" onClick={v.logout}>{v.t.dl.logout}</Button>
            </div>
            <h2 style={h2}>{v.t.dl.osTitle}</h2>
            <RadioCardGroup label={v.t.dl.osLabel} value={os && os.key} onChange={k => v.osList.find(o => o.key === k).select()} options={v.osList.map(o => ({ value: o.key, label: o.label, sub: o.sub }))} />
            <SpecList items={[[v.t.dl.file, v.file.name], [v.t.dl.size, v.file.size], [v.t.dl.version, v.file.version], [v.t.dl.sha, v.file.sha]]} />
            {v.dlIdle && <Button variant="galaxy" fullWidth trailing="↓" onClick={v.download} style={{ minHeight: 58 }}>{v.t.dl.dlBtn} · {v.file.os}</Button>}
            {v.dlLoading && <Button loading fullWidth style={{ minHeight: 58 }}>{v.t.dl.preparing}</Button>}
            {v.dlDone && <Notice title={v.t.dl.startedTitle} action={<Button size="sm" onClick={v.download} style={{ alignSelf: 'flex-start' }}>{v.t.dl.again}</Button>}>
              <p style={{ margin: 0 }}><strong style={{ fontWeight: 600 }}>{v.t.dl.installLabel}:</strong> {v.file.install}</p>
              <p style={{ margin: '10px 0 0', fontSize: 14, color: 'var(--sg-text)' }}>{v.t.dl.startedText}</p>
            </Notice>}
          </>}
        </Window>
        <aside style={{ display: 'flex', flexDirection: 'column', gap: 18 }}>
          <Window as="section">
            <h2 style={{ margin: '0 0 14px', fontWeight: 700, fontSize: 20 }}>{v.t.dl.whyTitle}</h2>
            <ul style={{ listStyle: 'none', margin: 0, padding: 0 }}>
              {v.t.dl.why.map((w, i) => <li key={i} style={{ padding: '10px 0', borderBottom: '1px solid var(--sg-line)', fontSize: 16, lineHeight: 1.5, color: 'var(--sg-title)', display: 'flex', gap: 12 }}><span aria-hidden="true" style={{ flex: 'none', marginTop: 7, width: 8, height: 8, borderRadius: '50%', background: 'radial-gradient(circle at 35% 35%,#FFFFFF,var(--sg-accent) 60%)', boxShadow: '0 0 8px 1px rgba(139,224,236,.55)' }} />{w}</li>)}
            </ul>
          </Window>
          <Window as="section" style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            <h2 style={{ margin: 0, fontWeight: 700, fontSize: 20 }}>{v.t.dl.reqTitle}</h2>
            <p style={{ margin: 0, fontSize: 16, lineHeight: 1.5 }}>{v.t.dl.reqText}</p>
            <Button size="sm" trailing="→" onClick={v.goFaq} style={{ alignSelf: 'flex-start', minHeight: 42 }}>{v.t.dl.reqBtn}</Button>
          </Window>
        </aside>
      </div>
    </PageWrap>
  );
};
