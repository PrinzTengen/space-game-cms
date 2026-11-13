const wrap = { maxWidth: 1240, margin: '0 auto', padding: 'clamp(40px,6vw,72px) clamp(20px,4vw,40px) clamp(64px,8vw,112px)' };
window.PageWrap = function PageWrap({ children, style }) { return <main style={{ ...wrap, ...style }}>{children}</main>; };

window.Header = function Header({ v }) {
  const { Navbar, Segment, Button, UserChip } = DS;
  return <Navbar badge={v.t.badge} navLabel={v.t.navLabel} onHome={v.goHome}
    items={v.nav.map(n => ({ label: n.label, active: n.active, onClick: n.go }))}
    right={<>
      <Segment bare size="sm" label={v.t.langLabel} value={v.lang} onChange={l => (l === 'de' ? v.setDE : v.setEN)()}
        options={[{ value: 'de', label: 'DE', lang: 'de' }, { value: 'en', label: 'EN', lang: 'en' }]} />
      {v.isIn ? <UserChip initials={v.user.initials} handle={v.user.handle} onClick={v.goDownload} />
        : <Button size="sm" caps onClick={v.goDownload}>{v.t.signIn}</Button>}
    </>} />;
};

window.SiteFooter = function SiteFooter({ v }) {
  return <DS.Footer line={v.t.foot.line} pagesLabel={v.t.foot.pages} rights={v.t.foot.rights} links={v.nav.map(n => ({ label: n.label, onClick: n.go }))} />;
};
