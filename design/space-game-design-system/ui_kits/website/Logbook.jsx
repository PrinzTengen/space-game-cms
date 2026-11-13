window.Logbook = function Logbook({ v, filter, setFilter }) {
  const { SectionHeader, Segment, PostCard } = DS;
  return (
    <PageWrap>
      <SectionHeader level="page" eyebrow={v.t.blog.label} title={v.t.blog.title} lead={v.t.blog.lead}
        action={<Segment label={v.t.blog.filterLabel} value={filter} onChange={setFilter} options={v.filters.map(f => ({ value: f.key, label: f.label, count: f.count }))} />} />
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill,minmax(min(100%,320px),1fr))', gap: 18 }}>
        {v.posts.map(p => <PostCard key={p.id} headingLevel="h2" title={p.title} excerpt={p.excerpt} typeLabel={p.typeLabel} date={p.date} iso={p.iso} read={p.read} more={v.t.blog.more} placeholder={v.t.blog.slot} onOpen={p.open} />)}
      </div>
    </PageWrap>
  );
};
