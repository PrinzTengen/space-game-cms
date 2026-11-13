class App extends React.Component {
  P = { prefix: 'kit', lang: { on: ['', ''], off: ['', ''] }, tab: { on: ['', ''], off: ['', ''] }, nav: { on: ['', ''], off: ['', ''] }, os: { on: ['', ''], off: ['', ''] },
    step: { done: ['', ''], current: ['', ''], pending: ['', ''] }, tag: { news: ['', ''], devlog: ['', ''] }, accents: ['', '', ''] };
  state = window.SG.initialState();
  render() {
    const v = window.SG.extra(window.SG.vals(this, this.P));
    const Page = { home: Home, blog: Logbook, article: Article, download: Download, faq: Faq }[this.state.page] || Home;
    return (
      <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', overflowX: 'hidden' }}>
        <Header v={v} />
        <div style={{ flex: '1 0 auto' }}><Page v={v} filter={this.state.filter} setFilter={f => this.setState({ filter: f })} /></div>
        <SiteFooter v={v} />
      </div>
    );
  }
}
window.getSpaceGameDS('../../').then(ns => { window.DS = ns; ReactDOM.createRoot(document.getElementById('root')).render(<App />); });
