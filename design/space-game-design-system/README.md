# Space Game – Design System

Design System für die Website des Weltraumspiels **Space Game** (Pre-Alpha, Windows & Linux, Zugang über Discord).
Grundlage ist die aktive Richtung **F2 Orbit** und die Kunden-Vorgabe vom 06.11.2026.

## Quellen
- `Space Game - Richtung F2 Orbit.dc.html` – aktive Richtung, Referenz für alle Werte
- `content.js` – Texte DE/EN, Beiträge, FAQ, Systemanforderungen, Download-Flow
- `space-game-bootstrap/` – Bootstrap-5.3-Theme (SCSS-Tokens, `sg-`-Komponenten, `galaxy.js`)
- `space-game-tailwind/` – Tailwind-Variante (v4 + v3)
- `CLAUDE.md` – Projektregeln und Kunden-Vorgabe
- Vergleichsrichtungen D, E, F (nicht maßgeblich)

## Produkt
Eine Marketing-/Community-Website mit fünf Seiten: Start, Logbuch (News & Devlogs), Beitrag, Download (Discord-Login → Plattform → Launcher) und System & FAQ. Zweisprachig DE/EN. Kein weiteres Produkt (kein In-Game-UI) in den Quellen.

---

## CONTENT FUNDAMENTALS
- **Ton:** ruhig, technisch, sachlich. Kein Hype, keine Ausrufezeichen. „Ein ruhiges, technisches Weltraumspiel.“
- **Anrede:** Du (DE) / you (EN). Das Team spricht als „wir“: „Wir erhalten nur deinen Benutzernamen und dein Avatar-Bild.“
- **Headlines:** kurz, imperativ oder als Aussage, mit Punkt: „Kartiere das Unbekannte.“, „Erkunden. Abbauen. Handeln.“
- **Eyebrows/Labels:** Versalien mit Sperrung, Trenner „ · “: „Erkundung · Handel · Ressourcenabbau“.
- **Buttons:** Verb + Objekt, Satzschreibung: „Launcher herunterladen“, „Devlogs lesen“, „Zum Download“. Pfeil-Glyph am Ende (→, ↓).
- **Zustände:** Ellipse mit Leerzeichen: „Verbinde mit Discord …“, „Download wird vorbereitet …“.
- **Zahlen & Technik:** konkret und ehrlich: „Build 0.4.2“, „84 MB“, „Vulkan 1.2“, „chmod +x“. Pre-Alpha-Einschränkungen offen benennen.
- **Begriffe:** „Logbuch“ statt Blog, „Devlog #7“, „Pre-Alpha“, „Launcher“. Discord-Kanäle als `#bug-reports`.
- **Emoji:** nie. Unicode nur als funktionale Glyphen (→ ← ↓ ✓ + − ·).

## VISUAL FOUNDATIONS
- **Farbe:** fast schwarzer, kühler Grund `#040a0e`. **Ein** Akzent `#8be0ec` (Eisblau) für Links, Eckwinkel, aktive Zustände, Pfeile, Fokus. Text in drei Stufen (#f2f7f8 / #c3d5d9 / #80a3ad). Signalfarben (#ffab26, #fc3624, #50f883) nur für Warnung/Gefahr/Erfolg. Warme Farben nur in Spielbildern und im Planet-Orb der Wortmarke.
- **Typo:** ausschließlich JetBrains Mono 400/600/700 (+500 für Bedienelemente), Ligaturen aus. Headlines 700, −0.01em, `text-wrap: balance`. Labels 11–12px Versal +0.12em, Hauptbutton 13px Versal +0.14em.
- **Hintergründe:** fester Sternenhintergrund (`assets/bg-stars.png`, Ausnahme auf Kundenwunsch). Hero vollflächig mit Key-Art, links abdunkelndem Scrim und einem leuchtenden Planetenrand am unteren Rand. Keine Verläufe als Dekor, keine Muster außer Scanlines.
- **Fenster (Karten):** 1px Rand `rgba(90,124,129,.6)`, 14px Eckwinkel in Akzent an allen vier Ecken, feine Scanlines (2px/3px), dunkles Glas `rgba(4,10,14,.84)`. Kein Schatten, kein Radius. Bildkarten haben 8px Innenabstand um das Bild.
- **Ecken:** `border-radius: 0` überall. Einzige Ausnahmen: runde Sterne/Status-Pips und der Planet-Orb. Der Hauptbutton hat eine 14px-Fase (clip-path), keine Rundung.
- **Hauptbutton „Galaxy“:** Glas-Verlauf in Hue 187, Sterne funkeln, bei Hover dreht sich ein Sternenring und HUD-Ecken leuchten auf. Max. einer pro Ansicht (Ausnahme auf Kundenwunsch).
- **Sekundärbuttons:** Fläche #0d242b, 1px Rand, Akzent-Text. Hover: Fläche #143d47, Rand Akzent, Text #a9ecf5. Pressed: 1px nach unten.
- **Hover:** Farbwechsel .15s; Karten heben sich 3px, Rand wird weiß 22% (.25s). Keine Opazitäts-Hovers.
- **Schatten:** nur `0 12px 30px -14px rgba(0,0,0,.9)` unter Buttons; Glühen nur Akzent (Galaxy-Hover, Footer-Linie, Pips) oder Erfolg.
- **Transparenz & Blur:** Header `rgba(18,24,27,.9)` + 12px Blur. Fenster als Glas über dem Sternenhintergrund. Sonst kein Blur.
- **Bildwelt:** kühles, dunkles Weltall, warmes Sonnen-/Planetenlicht nur im Bild. Bilder bekommen eine innere Vignette.
- **Layout:** Container 1240px, Rand clamp(20–40px), Raster mit `auto-fit/minmax` und 18px Abstand, Sektionen clamp(40–64px). Header sticky 64px, Hero überlappt ihn (−64px).
- **Bewegung:** Elemente blenden beim Scrollen ein (600ms, 14px, cubic-bezier(.2,.7,.2,1), 70ms Stagger). Keine Bounces. `prefers-reduced-motion` schaltet alles ab.
- **Fokus:** 2px Akzent-Outline, 3px Offset. Trefferflächen ≥ 44px.

## ICONOGRAPHY
- **Kein Icon-Set.** Die Quellen verwenden keine Icon-Font, keine SVG- oder PNG-Icons.
- Funktionale Unicode-Glyphen in JetBrains Mono: → ← ↓ (Richtung), + − (Akkordeon), ✓ (erledigt), · (Trenner). Pfeile stehen in Akzentfarbe.
- Status wird über kleine runde Pips mit Glühen gezeigt (`StatusDot`, `Tag`).
- Emoji werden nie verwendet.
- **Logo:** Es gibt keine Logo-Datei. Die Wortmarke ist der CSS-Planet-Orb + „Space Game“ in JetBrains Mono 700 (`Brand`). Bei echtem Logo bitte nachreichen.

---

## Index
- `styles.css` – Einstieg, nur `@import`s
- `tokens/` – `fonts.css`, `colors.css`, `typography.css`, `spacing.css`, `effects.css`, `base.css` (Body-Reset, Keyframes)
- `assets/` – `bg-stars.png`, `hero-keyart.png`, `cta-station.png`
- `guidelines/` – Grundlagen-Karten (Farben, Typo, Abstände, Effekte, Marke)
- `components/`
  - `actions/` – Button (galaxy, secondary, caps, loading), IconButton
  - `surfaces/` – Window, ImagePanel, MediaFrame
  - `navigation/` – Navbar, Brand, Segment, Footer
  - `content/` – Eyebrow, SectionHeader, Tag, PostCard, FeatureCard, Accordion/AccordionItem, SpecList, DataTable, UserChip/Avatar
  - `forms/` – RadioCard, RadioCardGroup
  - `feedback/` – Stepper, Notice, Spinner, StatusDot
- `ui_kits/website/` – klickbare Website (Start, Logbuch, Beitrag, Download, FAQ)
- `space-game-bootstrap/`, `space-game-tailwind/` – Umsetzungen für Produktion
- `SKILL.md` – Agent-Skill

### Intentional additions
- `SectionHeader` – bündelt das wiederkehrende Eyebrow + Titel + Aktion aus F2.
- `MediaFrame` – ersetzt die Bild-Slots aus F2 durch ein normales Bildelement mit Vignette.
- `Notice` warn/danger – F2 zeigt nur Erfolg; Varianten folgen der Signalfarben-Regel.

### Offen
- JetBrains-Mono-WOFF2 selbst hosten (aktuell Google Fonts).
- Echtes Logo fehlt.
