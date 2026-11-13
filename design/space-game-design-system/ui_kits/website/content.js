(function () {
const S = {
  de: {
    topbar: 'Space Game · Pre-Alpha · Build 0.4.2', langLabel: 'Sprache wählen', navLabel: 'Hauptnavigation',
    nav: { home: 'Start', blog: 'Logbuch', download: 'Download', faq: 'System & FAQ' },
    signIn: 'Anmelden', badge: 'Pre-Alpha', news: 'News', devlog: 'Devlog', minRead: 'Min. Lesezeit',
    home: {
      kicker: 'Erkundung · Handel · Ressourcenabbau', h1: 'Kartiere das Unbekannte.',
      lead: 'Ein ruhiges, technisches Weltraumspiel. Fliege in unerforschte Systeme, baue Rohstoffe ab und handle sie zwischen Stationen – in deinem eigenen Tempo.',
      cta: 'Launcher herunterladen', cta2: 'Devlogs lesen', note: 'Pre-Alpha für Windows & Linux · Anmeldung über Discord',
      fig: 'Abb. 1 — Key-Art', slot: 'Key-Art hier ablegen',
      pillarsLabel: 'Das Spiel in drei Teilen', pillarsTitle: 'Erkunden. Abbauen. Handeln.',
      latestLabel: 'Logbuch', latestTitle: 'Neu aus der Entwicklung', all: 'Alle Beiträge',
      ctaTitle: 'Bereit für den ersten Start?', ctaText: 'Melde dich mit Discord an und lade den Launcher für Windows oder Linux herunter.', ctaBtn: 'Zum Download'
    },
    pillars: [
      { n: '01', title: 'Erkunden', text: 'Springe in Systeme, die noch niemand kartiert hat. Jeder Scan füllt deine Sternkarte.' },
      { n: '02', title: 'Abbauen', text: 'Analysiere Asteroiden, bevor du bohrst. Jeder Brocken hat eine eigene Zusammensetzung.' },
      { n: '03', title: 'Handeln', text: 'Stationen haben unterschiedlichen Bedarf. Wer Wege und Preise kennt, verdient am meisten.' }
    ],
    blog: { label: 'News & Devlogs', title: 'Logbuch', lead: 'Ankündigungen, Patch-Notes und Einblicke in die Entwicklung.', filterLabel: 'Beiträge filtern', all: 'Alle', news: 'News', devlog: 'Devlogs', more: 'Weiterlesen', slot: 'Bild ablegen' },
    art: { back: 'Zurück zum Logbuch', next: 'Nächster Beitrag', slot: 'Beitragsbild ablegen' },
    dl: {
      label: 'Download', title: 'Launcher',
      lead: 'Der Launcher installiert das Spiel und hält es aktuell. Für den Pre-Alpha-Zugang meldest du dich einmalig mit Discord an.',
      steps: ['Mit Discord anmelden', 'Plattform wählen', 'Herunterladen & installieren'],
      done: 'Erledigt', current: 'Aktuell', pending: 'Offen', step: 'Schritt',
      loginTitle: 'Mit Discord anmelden',
      loginText: 'Der Download ist für angemeldete Tester freigeschaltet. Du wirst zu Discord weitergeleitet und kommst danach direkt hierher zurück.',
      loginBtn: 'Mit Discord anmelden', connecting: 'Verbinde mit Discord …',
      privacy: 'Wir erhalten nur deinen Benutzernamen und dein Avatar-Bild.',
      signedIn: 'Angemeldet als', logout: 'Abmelden', osTitle: 'Plattform wählen', osLabel: 'Betriebssystem',
      file: 'Datei', size: 'Größe', version: 'Version', sha: 'SHA-256',
      dlBtn: 'Herunterladen', preparing: 'Download wird vorbereitet …',
      startedTitle: 'Download gestartet', startedText: 'Startet der Download nicht automatisch, versuche es erneut.', again: 'Erneut herunterladen',
      installLabel: 'Installation', install: { win: 'Setup-Datei ausführen und den Anweisungen folgen.', linux: 'Datei ausführbar machen (chmod +x) und starten.' },
      whyTitle: 'Warum Discord?', why: ['Pre-Alpha-Zugang ohne zusätzliches Konto', 'Feedback und Bug-Reports an einem Ort', 'Ankündigungen zu neuen Builds'],
      reqTitle: 'Läuft es bei dir?', reqText: 'Mindestens 8 GB RAM und eine Grafikkarte mit Vulkan 1.2.', reqBtn: 'Systemanforderungen ansehen',
      msgIn: 'Erfolgreich mit Discord angemeldet.', msgOut: 'Du wurdest abgemeldet.', msgDl: 'Download gestartet.'
    },
    faq: { label: 'Support', title: 'System & FAQ', reqTitle: 'Systemanforderungen', comp: 'Komponente', min: 'Minimum', rec: 'Empfohlen', reqNote: 'Pre-Alpha: Die Anforderungen können sich bis zum Release noch ändern.', faqTitle: 'Häufige Fragen' },
    foot: { line: 'Ein Weltraumspiel über Erkundung, Handel und Ressourcenabbau.', pages: 'Seiten', rights: '© 2026 Space Game · Pre-Alpha' }
  },
  en: {
    topbar: 'Space Game · Pre-Alpha · Build 0.4.2', langLabel: 'Choose language', navLabel: 'Main navigation',
    nav: { home: 'Home', blog: 'Logbook', download: 'Download', faq: 'System & FAQ' },
    signIn: 'Sign in', badge: 'Pre-Alpha', news: 'News', devlog: 'Devlog', minRead: 'min read',
    home: {
      kicker: 'Exploration · Trade · Mining', h1: 'Chart the unknown.',
      lead: 'A calm, technical space game. Fly into uncharted systems, mine resources and trade them between stations – at your own pace.',
      cta: 'Download launcher', cta2: 'Read devlogs', note: 'Pre-Alpha for Windows & Linux · Sign in with Discord',
      fig: 'Fig. 1 — Key art', slot: 'Drop key art here',
      pillarsLabel: 'The game in three parts', pillarsTitle: 'Explore. Mine. Trade.',
      latestLabel: 'Logbook', latestTitle: 'Fresh from development', all: 'All posts',
      ctaTitle: 'Ready for your first launch?', ctaText: 'Sign in with Discord and download the launcher for Windows or Linux.', ctaBtn: 'Go to download'
    },
    pillars: [
      { n: '01', title: 'Explore', text: 'Jump into systems nobody has charted yet. Every scan fills in your star map.' },
      { n: '02', title: 'Mine', text: 'Analyse asteroids before you drill. Every rock has its own composition.' },
      { n: '03', title: 'Trade', text: 'Stations need different things. Know the routes and prices, and you earn the most.' }
    ],
    blog: { label: 'News & Devlogs', title: 'Logbook', lead: 'Announcements, patch notes and a look behind the scenes.', filterLabel: 'Filter posts', all: 'All', news: 'News', devlog: 'Devlogs', more: 'Read more', slot: 'Drop image' },
    art: { back: 'Back to logbook', next: 'Next post', slot: 'Drop cover image' },
    dl: {
      label: 'Download', title: 'Launcher',
      lead: 'The launcher installs the game and keeps it up to date. For Pre-Alpha access, sign in once with Discord.',
      steps: ['Sign in with Discord', 'Choose platform', 'Download & install'],
      done: 'Done', current: 'Current', pending: 'Pending', step: 'Step',
      loginTitle: 'Sign in with Discord',
      loginText: 'The download is unlocked for signed-in testers. You will be redirected to Discord and brought straight back here.',
      loginBtn: 'Sign in with Discord', connecting: 'Connecting to Discord …',
      privacy: 'We only receive your username and avatar.',
      signedIn: 'Signed in as', logout: 'Sign out', osTitle: 'Choose platform', osLabel: 'Operating system',
      file: 'File', size: 'Size', version: 'Version', sha: 'SHA-256',
      dlBtn: 'Download', preparing: 'Preparing download …',
      startedTitle: 'Download started', startedText: 'If the download does not start automatically, try again.', again: 'Download again',
      installLabel: 'Installation', install: { win: 'Run the setup file and follow the instructions.', linux: 'Make the file executable (chmod +x) and run it.' },
      whyTitle: 'Why Discord?', why: ['Pre-Alpha access without another account', 'Feedback and bug reports in one place', 'Announcements for new builds'],
      reqTitle: 'Will it run?', reqText: 'At least 8 GB RAM and a graphics card with Vulkan 1.2.', reqBtn: 'View system requirements',
      msgIn: 'Signed in with Discord.', msgOut: 'You have been signed out.', msgDl: 'Download started.'
    },
    faq: { label: 'Support', title: 'System & FAQ', reqTitle: 'System requirements', comp: 'Component', min: 'Minimum', rec: 'Recommended', reqNote: 'Pre-Alpha: requirements may still change before release.', faqTitle: 'Frequently asked questions' },
    foot: { line: 'A space game about exploration, trade and mining.', pages: 'Pages', rights: '© 2026 Space Game · Pre-Alpha' }
  }
};

const POSTS = [
  { id: 'devlog-7', type: 'devlog', num: 7, date: '2026-10-30', read: 6,
    de: { title: 'Prozedurale Asteroidenfelder', excerpt: 'Wie wir Felder erzeugen, die dicht wirken und trotzdem navigierbar bleiben – und warum jeder Brocken jetzt eine echte Zusammensetzung hat.',
      body: [['p', 'Asteroidenfelder sind der Ort, an dem Erkundung und Abbau zusammenkommen. In früheren Builds waren sie reine Kulisse. Mit 0.4 ändert sich das.'], ['h', 'Dichte ohne Chaos'], ['p', 'Jedes Feld entsteht aus wenigen Clustern mit klaren Korridoren dazwischen. So bleibt Platz zum Manövrieren, während das Feld aus der Ferne dicht wirkt.'], ['img', 'Abb. — Cluster und Korridore im Testfeld'], ['h', 'Was im Gestein steckt'], ['p', 'Jeder Asteroid enthält bis zu drei Rohstoffe. Der Scanner zeigt sie an, bevor du bohrst – Abbau wird zur Entscheidung, nicht zur Fleißarbeit.']] },
    en: { title: 'Procedural asteroid fields', excerpt: 'How we generate fields that feel dense yet stay navigable – and why every rock now has a real composition.',
      body: [['p', 'Asteroid fields are where exploration and mining meet. In earlier builds they were scenery. With 0.4 that changes.'], ['h', 'Density without chaos'], ['p', 'Each field is built from a few clusters with clear corridors in between. That leaves room to manoeuvre while the field still looks dense from afar.'], ['img', 'Fig. — Clusters and corridors in the test field'], ['h', 'What is inside the rock'], ['p', 'Every asteroid holds up to three resources. The scanner shows them before you drill – mining becomes a decision, not a chore.']] } },
  { id: 'news-0-4', type: 'news', date: '2026-10-22', read: 3,
    de: { title: 'Pre-Alpha 0.4 ist verfügbar', excerpt: 'Neue Asteroidenfelder, überarbeiteter Handel und ein Launcher, der Updates selbst einspielt.',
      body: [['p', 'Build 0.4.2 steht ab sofort im Launcher bereit. Ist das Spiel bereits installiert, aktualisiert es sich beim nächsten Start automatisch.'], ['h', 'Die wichtigsten Änderungen'], ['p', 'Prozedurale Asteroidenfelder mit Rohstoff-Zusammensetzung, eine neue Preisberechnung an Stationen, überarbeitete Cockpit-Anzeigen und zahlreiche Fehlerbehebungen.'], ['p', 'Fehler meldest du am besten im Discord-Kanal #bug-reports – gern mit der Logdatei aus dem Launcher.']] },
    en: { title: 'Pre-Alpha 0.4 is available', excerpt: 'New asteroid fields, reworked trading and a launcher that installs updates by itself.',
      body: [['p', 'Build 0.4.2 is now available in the launcher. If the game is already installed, it updates automatically on next launch.'], ['h', 'Key changes'], ['p', 'Procedural asteroid fields with resource composition, new price calculation at stations, reworked cockpit displays and many bug fixes.'], ['p', 'Please report bugs in the Discord channel #bug-reports – ideally with the log file from the launcher.']] } },
  { id: 'devlog-6', type: 'devlog', num: 6, date: '2026-10-09', read: 8,
    de: { title: 'Wie Preise zwischen Stationen entstehen', excerpt: 'Angebot, Nachfrage und Entfernung: ein Blick in das Wirtschaftsmodell hinter dem Handel.',
      body: [['p', 'Handel soll sich lohnen, ohne berechenbar zu werden. Jede Station hat deshalb einen eigenen Bedarf, der sich mit der Zeit verschiebt.'], ['h', 'Drei Faktoren'], ['p', 'Der Preis eines Rohstoffs ergibt sich aus dem Lagerbestand der Station, ihrem Verbrauch und der Entfernung zur nächsten Quelle. Wer weite Wege fliegt, wird belohnt.'], ['p', 'In der Pre-Alpha sind die Werte bewusst grob eingestellt. Euer Feedback hilft uns, die Balance zu finden.']] },
    en: { title: 'How prices form between stations', excerpt: 'Supply, demand and distance: a look at the economic model behind trading.',
      body: [['p', 'Trading should pay off without becoming predictable. That is why every station has its own demand, which shifts over time.'], ['h', 'Three factors'], ['p', 'A resource price depends on the station’s stock, its consumption and the distance to the nearest source. Long hauls are rewarded.'], ['p', 'In the Pre-Alpha the values are deliberately rough. Your feedback helps us find the balance.']] } },
  { id: 'news-discord', type: 'news', date: '2026-09-25', read: 2,
    de: { title: 'Unser Discord-Server ist offen', excerpt: 'Der Pre-Alpha-Zugang läuft ab sofort über Discord. So kommst du rein.',
      body: [['p', 'Für die Pre-Alpha nutzen wir Discord als zentralen Ort für Zugang, Feedback und Ankündigungen.'], ['p', 'Melde dich auf der Download-Seite mit deinem Discord-Konto an, um den Launcher herunterzuladen. Danach findest du uns in den Kanälen #feedback und #bug-reports.']] },
    en: { title: 'Our Discord server is open', excerpt: 'Pre-Alpha access now runs through Discord. Here is how to get in.',
      body: [['p', 'For the Pre-Alpha we use Discord as the central place for access, feedback and announcements.'], ['p', 'Sign in with your Discord account on the download page to get the launcher. Afterwards, find us in #feedback and #bug-reports.']] } },
  { id: 'devlog-5', type: 'devlog', num: 5, date: '2026-09-11', read: 5,
    de: { title: 'Instrumente im Cockpit', excerpt: 'Analoge Anzeigen, klare Skalen: warum unser HUD aussieht wie aus einem Handbuch von 1975.',
      body: [['p', 'Im Cockpit verbringst du die meiste Zeit. Deshalb soll jede Anzeige auf einen Blick lesbar sein.'], ['h', 'Weniger, aber deutlicher'], ['p', 'Wir haben die Zahl der Anzeigen halbiert und setzen auf große Skalen, feste Positionen und eine einzige Warnfarbe.'], ['img', 'Abb. — Entwurf der Treibstoffanzeige']] },
    en: { title: 'Instruments in the cockpit', excerpt: 'Analogue gauges, clear scales: why our HUD looks like it came from a 1975 manual.',
      body: [['p', 'You spend most of your time in the cockpit, so every display should be readable at a glance.'], ['h', 'Fewer, but clearer'], ['p', 'We halved the number of displays and rely on large scales, fixed positions and a single warning colour.'], ['img', 'Fig. — Draft of the fuel gauge']] } }
];

const REQ = [
  { l: { de: 'Betriebssystem', en: 'Operating system' }, min: 'Windows 10 64-bit / Ubuntu 22.04', rec: 'Windows 11 / Ubuntu 24.04' },
  { l: { de: 'Prozessor', en: 'Processor' }, min: { de: '4 Kerne, 3,0 GHz', en: '4 cores, 3.0 GHz' }, rec: { de: '6 Kerne, 3,6 GHz', en: '6 cores, 3.6 GHz' } },
  { l: { de: 'Arbeitsspeicher', en: 'Memory' }, min: '8 GB', rec: '16 GB' },
  { l: { de: 'Grafik', en: 'Graphics' }, min: 'GTX 1060 / RX 580 · Vulkan 1.2', rec: 'RTX 2070 / RX 6600' },
  { l: { de: 'Speicher', en: 'Storage' }, min: '20 GB SSD', rec: '20 GB NVMe SSD' },
  { l: { de: 'Internet', en: 'Internet' }, min: { de: 'Für Anmeldung & Updates', en: 'For sign-in & updates' }, rec: { de: 'Für Anmeldung & Updates', en: 'For sign-in & updates' } }
];

const FAQ = {
  de: [
    ['Warum brauche ich ein Discord-Konto?', 'Über Discord vergeben wir den Pre-Alpha-Zugang und sammeln Feedback. So brauchst du kein weiteres Konto bei uns.'],
    ['Gibt es eine macOS-Version?', 'Aktuell unterstützt der Launcher Windows und Linux.'],
    ['Wie installiere ich den Launcher unter Linux?', 'Lade die AppImage-Datei herunter, mache sie mit „chmod +x“ ausführbar und starte sie. Eine Installation ist nicht nötig.'],
    ['Bleibt mein Spielstand bei Updates erhalten?', 'In der Pre-Alpha können Spielstände bei größeren Updates zurückgesetzt werden. Wir kündigen das vorher im Logbuch an.'],
    ['Wo melde ich Fehler?', 'Im Discord-Kanal #bug-reports. Hänge am besten die Logdatei an, die du im Launcher unter „Hilfe“ findest.']
  ],
  en: [
    ['Why do I need a Discord account?', 'We grant Pre-Alpha access and collect feedback through Discord, so you don’t need another account with us.'],
    ['Is there a macOS version?', 'The launcher currently supports Windows and Linux.'],
    ['How do I install the launcher on Linux?', 'Download the AppImage, make it executable with “chmod +x” and run it. No installation required.'],
    ['Will my save survive updates?', 'During Pre-Alpha, saves may be reset with larger updates. We announce this in the logbook beforehand.'],
    ['Where do I report bugs?', 'In the Discord channel #bug-reports. Please attach the log file found in the launcher under “Help”.']
  ]
};

const OS = [
  { key: 'win', label: 'Windows', sub: 'Windows 10 / 11 · 64-bit', file: 'SpaceGame-Launcher-Setup-0.4.2.exe', size: '84 MB', sha: '9c1f 3b7a … e47a' },
  { key: 'linux', label: 'Linux', sub: 'x86_64 · AppImage', file: 'SpaceGame-Launcher-0.4.2.AppImage', size: '91 MB', sha: '4d8e a012 … 7c3b' }
];

const PAGES = ['home', 'blog', 'article', 'download', 'faq'];
const LS = (k, v) => { try { if (v === undefined) return localStorage.getItem(k); localStorage.setItem(k, v); } catch (e) { return null; } };
const fmt = (d, l) => new Intl.DateTimeFormat(l === 'de' ? 'de-DE' : 'en-GB', { day: '2-digit', month: 'short', year: 'numeric' }).format(new Date(d + 'T12:00:00'));
const pick = (pair, on) => { const c = on ? pair.on : pair.off; return { bg: c[0], fg: c[1] }; };

function initialState() {
  const p = LS('sg-page');
  const ua = navigator.userAgent || '';
  return {
    page: PAGES.includes(p) ? p : 'home', lang: LS('sg-lang') === 'en' ? 'en' : 'de', filter: 'all',
    postId: POSTS.some(x => x.id === LS('sg-post')) ? LS('sg-post') : POSTS[0].id,
    auth: LS('sg-auth') === 'in' ? 'in' : 'out', os: /linux/i.test(ua) && !/android/i.test(ua) ? 'linux' : 'win',
    dl: 'idle', faqOpen: 0, msg: ''
  };
}

function vals(c, P) {
  const s = c.state, L = s.lang, t = S[L];
  const set = o => c.setState(o);
  const go = (page, extra) => () => {
    const o = Object.assign({ page, dl: 'idle', msg: '' }, extra || {});
    set(o); LS('sg-page', page); if (o.postId) LS('sg-post', o.postId);
    window.scrollTo(0, 0);
  };
  const r = v => (typeof v === 'string' ? v : v[L]);
  const mapPost = p => {
    const x = p[L], tg = P.tag[p.type];
    return { id: p.id, title: x.title, excerpt: x.excerpt, date: fmt(p.date, L), iso: p.date,
      typeLabel: p.type === 'devlog' ? t.devlog + ' #' + p.num : t.news, isDevlog: p.type === 'devlog',
      read: p.read + ' ' + t.minRead, slotId: P.prefix + '-post-' + p.id, tagBg: tg[0], tagFg: tg[1],
      open: go('article', { postId: p.id }) };
  };
  const all = POSTS.map(mapPost);
  const idx = Math.max(0, POSTS.findIndex(p => p.id === s.postId));
  const cur = POSTS[idx], nextP = POSTS[(idx + 1) % POSTS.length];
  const navDef = [['home', 'home'], ['blog', 'blog'], ['download', 'download'], ['faq', 'faq']];
  const activeNav = s.page === 'article' ? 'blog' : s.page;
  const filters = [['all', t.blog.all], ['news', t.blog.news], ['devlog', t.blog.devlog]].map(([k, label]) => {
    const on = s.filter === k;
    return Object.assign({ key: k, label, pressed: on ? 'true' : 'false', count: k === 'all' ? POSTS.length : POSTS.filter(p => p.type === k).length, select: () => set({ filter: k }) }, pick(P.tab, on));
  });
  const stepState = [s.auth === 'in' ? 'done' : 'current', s.auth !== 'in' ? 'pending' : (s.dl === 'done' ? 'done' : 'current'), s.dl === 'done' ? 'current' : 'pending'];
  const os = OS.find(o => o.key === s.os) || OS[0];
  const lang = (k) => pick(P.lang, L === k);
  return {
    ready: true, t, lang: L,
    setDE: () => { set({ lang: 'de' }); LS('sg-lang', 'de'); document.documentElement.lang = 'de'; },
    setEN: () => { set({ lang: 'en' }); LS('sg-lang', 'en'); document.documentElement.lang = 'en'; },
    deP: L === 'de' ? 'true' : 'false', enP: L === 'en' ? 'true' : 'false',
    deBg: lang('de').bg, deFg: lang('de').fg, enBg: lang('en').bg, enFg: lang('en').fg,
    nav: navDef.map(([k]) => Object.assign({ key: k, label: t.nav[k], active: activeNav === k, cur: activeNav === k ? 'page' : undefined, go: go(k) }, pick(P.nav, activeNav === k))),
    isHome: s.page === 'home', isBlog: s.page === 'blog', isArticle: s.page === 'article', isDownload: s.page === 'download', isFaq: s.page === 'faq',
    goHome: go('home'), goBlog: go('blog'), goDownload: go('download'), goFaq: go('faq'),
    goDevlogs: () => { go('blog')(); set({ filter: 'devlog' }); },
    pillars: t.pillars.map((p, i) => Object.assign({ accent: P.accents[i % P.accents.length] }, p)),
    latest: all.slice(0, 3),
    posts: all.filter(p => s.filter === 'all' || POSTS.find(x => x.id === p.id).type === s.filter),
    filters,
    article: Object.assign(mapPost(cur), {
      blocks: cur[L].body.map((b, i) => ({ isP: b[0] === 'p', isH: b[0] === 'h', isImg: b[0] === 'img', text: b[1], slotId: P.prefix + '-art-' + cur.id + '-' + i }))
    }),
    next: mapPost(nextP),
    isOut: s.auth === 'out', isLoading: s.auth === 'loading', isIn: s.auth === 'in', notIn: s.auth !== 'in',
    user: { name: 'Nova Kepler', handle: '@nova_kepler', initials: 'NK' },
    login: () => { set({ auth: 'loading', msg: t.dl.connecting }); setTimeout(() => { set({ auth: 'in', msg: S[c.state.lang].dl.msgIn }); LS('sg-auth', 'in'); }, 1400); },
    logout: () => { set({ auth: 'out', dl: 'idle', msg: t.dl.msgOut }); LS('sg-auth', 'out'); },
    steps: t.dl.steps.map((label, i) => Object.assign({ n: '0' + (i + 1), label, status: t.dl[stepState[i]], isDone: stepState[i] === 'done' }, pick({ on: P.step[stepState[i]], off: P.step[stepState[i]] }, true))),
    osList: OS.map(o => Object.assign({ key: o.key, label: o.label, sub: o.sub, checked: s.os === o.key ? 'true' : 'false', active: s.os === o.key, select: () => set({ os: o.key, dl: 'idle' }) }, pick(P.os, s.os === o.key))),
    file: { name: os.file, size: os.size, sha: os.sha, version: '0.4.2 Pre-Alpha', install: t.dl.install[os.key], os: os.label },
    download: () => { set({ dl: 'loading', msg: t.dl.preparing }); setTimeout(() => set({ dl: 'done', msg: S[c.state.lang].dl.msgDl }), 900); },
    dlIdle: s.dl === 'idle', dlLoading: s.dl === 'loading', dlDone: s.dl === 'done',
    msg: s.msg,
    reqRows: REQ.map(x => ({ label: r(x.l), min: r(x.min), rec: r(x.rec) })),
    faqs: FAQ[L].map(([q, a], i) => ({ q, a, id: P.prefix + '-faq-' + i, btnId: P.prefix + '-faqb-' + i, open: s.faqOpen === i, exp: s.faqOpen === i ? 'true' : 'false', sign: s.faqOpen === i ? '−' : '+', toggle: () => set({ faqOpen: s.faqOpen === i ? -1 : i }) }))
  };
}

function boot(inst) {
  const wait = () => {
    const s = initialState(); document.documentElement.lang = s.lang; inst.setState(s);
  };
  wait();
}
function reveal(inst) {
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches || !window.IntersectionObserver) return;
  if (!inst._io) inst._io = new IntersectionObserver(es => es.forEach(e => {
    if (!e.isIntersecting) return;
    const el = e.target; inst._io.unobserve(el);
    const d = Math.min(+el.getAttribute('data-reveal') || 0, 8) * 70;
    el.style.opacity = '';
    el.animate([{ opacity: 0, transform: 'translateY(14px)' }, { opacity: 1, transform: 'none' }], { duration: 600, delay: d, easing: 'cubic-bezier(.2,.7,.2,1)', fill: 'backwards' });
  }), { threshold: 0.08 });
  document.querySelectorAll('[data-reveal]:not([data-rv])').forEach(el => {
    el.setAttribute('data-rv', '1'); el.style.opacity = '0'; inst._io.observe(el);
    setTimeout(() => { if (el.style.opacity === '0') el.style.opacity = ''; }, 2500);
  });
}
function extra(v) {
  v.steps.forEach(s => { s.isCurrent = s.status === v.t.dl.current; s.isPending = s.status === v.t.dl.pending; });
  return Object.assign(v, { s1: v.steps[0], s2: v.steps[1], s3: v.steps[2], feature: v.latest[0], rest: v.latest.slice(1), firstPost: v.posts[0], morePosts: v.posts.slice(1), hasMore: v.posts.length > 1 });
}

window.SG = { initialState, vals, boot, reveal, extra };
})();
