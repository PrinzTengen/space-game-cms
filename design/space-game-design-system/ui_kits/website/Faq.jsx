window.Faq = function Faq({ v }) {
  const { SectionHeader, Window, DataTable, Accordion } = DS;
  return (
    <PageWrap>
      <SectionHeader level="page" eyebrow={v.t.faq.label} title={v.t.faq.title} />
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(min(100%,460px),1fr))', gap: 18, alignItems: 'start' }}>
        <Window as="section">
          <h2 style={{ margin: '0 0 18px', fontWeight: 700, fontSize: 23 }}>{v.t.faq.reqTitle}</h2>
          <DataTable columns={[v.t.faq.comp, v.t.faq.min, v.t.faq.rec]} rows={v.reqRows.map(r => [r.label, r.min, r.rec])} />
          <p style={{ margin: '14px 0 0', fontSize: 12, color: 'var(--sg-dim)' }}>{v.t.faq.reqNote}</p>
        </Window>
        <section>
          <h2 style={{ margin: '0 0 18px', fontWeight: 700, fontSize: 23 }}>{v.t.faq.faqTitle}</h2>
          <Accordion key={v.lang} items={v.faqs.map(f => ({ q: f.q, a: f.a }))} />
        </section>
      </div>
    </PageWrap>
  );
};
