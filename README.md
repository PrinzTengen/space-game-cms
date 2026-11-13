# Space Game

website

## F2 Orbit: übernommenes Designsystem

Die ZIP **Gestaltungsrichtlinien und Spielprojekt.zip** ist unverändert unter
`design/space-game-design-system/` abgelegt. Ihre Tokens, Motive und das Website-
UI-Kit sind die Referenz für die Django-Umsetzung. Die Original-React-Dateien
bleiben als Referenz erhalten; die Website rendert native Django-/CMS-Templates.

Übernommen sind Sternenhintergrund, Key-Art, CTA-Bild, Farb- und Typografiewerte,
der Planet-Orb, Glasfenster mit Eckwinkeln und Scanlines, der Galaxy-Button mit
Sternen und Umlaufbahn sowie Scroll-Reveals. JetBrains Mono 400/500/600/700 bleibt
lokal über npm eingebunden. `npm run build` kopiert die drei Originalmotive nach
`static/build/design-system/`; es werden keine Font- oder React-CDNs geladen.

Das UI-Kit ist auf Startseite, Logbuch, Beitragsseite, Download und System & FAQ
übertragen. Die zuletzt ergänzte Galerie bleibt als CMS-Erweiterung unter dem
CTA erhalten und verwendet die neuen Fenster- und Bedienelemente. Admin und
CMS-Toolbar übernehmen Schrift, Farben, eckige Flächen und die neue Wortmarke.

Nach Installation der Abhängigkeiten und `migrate`:

```bash
docker compose -f docker-compose.local.yml exec django python manage.py apply_design_system --username DEIN_ADMIN
```

Der Befehl übernimmt die gelieferten DE-/EN-Inhalte, die fünf Beiträge, die
Download- und FAQ-Seiten. Änderungen an bestehenden Startseiten werden als neue
Version veröffentlicht. Geänderte unveröffentlichte Entwürfe werden geschützt;
ein erneuter Aufruf überschreibt nach der ersten Übernahme keine redaktionellen
Änderungen. Die Quellen der Texte liegen in `space_game/theme/design_content.json`.
Die Sprachauswahl arbeitet mit Djangos Sprach-Cookie.

Die ZIP enthält keine Launcher-Dateien. Der Download ist öffentlich und benötigt
weder Anmeldung noch Discord-Konto. Im jeweiligen **Space Game Launcher Platform**-
Plugin lässt sich unter **Launcher file** eine Datei über django-filer auswählen
oder direkt per Drag-and-drop hochladen. Alternativ können eine externe HTTPS-URL
im Plugin oder Standard-URLs in der Django-Umgebung verwendet werden:

```dotenv
SPACE_GAME_WINDOWS_DOWNLOAD_URL=
SPACE_GAME_LINUX_DOWNLOAD_URL=
```

Die ausgewählte Datei hat Vorrang vor Plugin-URL und Umgebungswert. Dateiname und
Größe werden bei hochgeladenen Dateien automatisch aus der Datei übernommen;
der Download erfolgt ohne Anmeldung als Anhang mit dem Originaldateinamen.
Dateien müssen in django-filer öffentlich sein. Ohne Datei oder gültige URL zeigt
das Plattform-Plugin den bearbeitbaren Verfügbarkeitshinweis. Version und
vollständige SHA-256-Prüfsumme können passend zur Datei ergänzt werden.
Discord bleibt eine freiwillige Community.

## django CMS

### FAQ und Systemanforderungen als eigenständige Plugins

**Space Game FAQ** ist ein eigenständiges `djangocms-frontend`-Plugin und kann
auch auf anderen CMS-Seiten eingefügt werden. Überschrift, Einleitung und die
Option „Only open one answer at a time“ liegen im Gruppen-Plugin. Darunter werden
beliebig viele **Space Game FAQ Item**-Plugins mit Frage, Antwort und „Open
initially“ eingefügt, sortiert oder gelöscht. Antworten unterstützen Absätze und
werden als Text sicher ausgegeben. Jede FAQ-Gruppe besitzt ihren eigenen
Akkordeon-Namen; mehrere Gruppen beeinflussen sich nicht gegenseitig. Das
Akkordeon funktioniert ohne JavaScript. Im CMS-Editor sind alle Antworten offen.

Auf `/faq/` enthält die Vorlage ausschließlich Layout und Platzhalter:

- `support_header`: **Space Game Support Header** mit Vorspann, Titel und Untertitel.
- `system_requirements`: **Space Game System Requirements** mit einzelnen **System Requirement**-Zeilen.
- `faq`: **Space Game FAQ** mit den Frage-Antwort-Einträgen.
- `content`: zusätzliche CMS-Inhalte.

Auch die Tabellenüberschriften, Anforderungen und der Hinweistext sind im CMS
bearbeitbar. Vorhandene DE-/EN-Texte werden einmalig als versionierte Plugins
übernommen; spätere Änderungen erfolgen im CMS. Nach `migrate`:

```bash
docker compose -f docker-compose.local.yml exec django python manage.py install_faq_plugins --username DEIN_ADMIN
```

Der Installer schützt bearbeitete Entwürfe und bestehende Plugin-Inhalte.
`apply_design_system` ruft ihn bei neuen Installationen automatisch auf.

### Downloadseite vollständig als Frontend-Plugins

Die Vorlage `cms/download.html` enthält nur das Layout und CMS-Platzhalter:

- `download_header`: **Space Game Download Header**, mit Vorspann, Titel und Untertitel.
- `download_steps`: **Space Game Download Steps** mit einzelnen **Download Step**-Kindern.
- `launcher`: **Space Game Launcher Downloads** mit **Launcher Platform**-Kindern für Windows/Linux.
- `download_sidebar`: beliebig viele **Space Game Download Info**-Boxen mit Text, Liste und optionalem Link.
- `content`: zusätzliche CMS-Inhalte.

Im Launcher-Plugin werden die Überschrift, Feldbezeichnungen, Buttontexte und
der Verfügbarkeitshinweis bearbeitet. Im jeweiligen Plattform-Kind liegen Datei,
alternative URL, Dateiname, Größe, Version, Prüfsumme und Installationsanleitung. Alle Inhalte sind
versioniert und pro Sprache bearbeitbar; veröffentlichte Download-URLs sind für
Besucher ohne Login erreichbar. Unveröffentlichte URL-Änderungen bleiben privat.
Eine leere URL verwendet den Umgebungswert; eine ungültige URL bleibt gesperrt.

Bestehende Seiten nach `migrate` überführen:

```bash
docker compose -f docker-compose.local.yml exec django python manage.py install_download_plugins --username DEIN_ADMIN
```

`apply_design_system` führt diesen Installer für neue Installationen automatisch
aus. Bestehende Plugin-Inhalte und bearbeitete Entwürfe werden geschützt.
Unveränderte Standardtexte auf der Startseite, die eine Anmeldung verlangen,
werden ebenfalls korrigiert; eigene Texte bleiben erhalten. Die Plattformwahl
verwendet JavaScript ohne Seitenneuladen und merkt sich `?platform=linux` in der
URL. Ohne JavaScript und im CMS-Editor bleiben alle Plattformen sichtbar.

### Logbuch: bearbeitbarer Header und Live-Suche

Auf `/stories/` lassen sich Vorspann, Überschrift und Untertitel über das
`djangocms-frontend`-Plugin **Space Game Logbook Header** im Platzhalter
`logbook_header` bearbeiten, jeweils getrennt für Deutsch und Englisch.
Änderungen werden als CMS-Entwurf gespeichert und nach Veröffentlichung sichtbar.
Die Seitenvorlage **Space Game — Logbook** stellt den Header auch im CMS-Editor dar.
Auf der öffentlichen Logbuchseite verknüpft eine Middleware die Stories-Übersicht
mit ihrer CMS-Seite, damit die Toolbar **New Draft / Neuer Entwurf** bzw.
**Edit / Bearbeiten** anbietet. Diesen Button anklicken, dann den Header doppelt
anklicken. Speichern und anschließend veröffentlichen.

Bestehende Logbuchseiten einmal mit `migrate` und folgendem Befehl überführen:

```bash
docker compose -f docker-compose.local.yml exec django python manage.py install_logbook_header --username DEIN_ADMIN
```

Neue Installationen erhalten den Header automatisch. Der Befehl ist wiederholbar
und schützt bearbeitete, unveröffentlichte Entwürfe.

Die JavaScript-Suche filtert die veröffentlichten Beiträge anhand von Titel,
Untertitel, Einleitung, vollständigem Text und Schlagwörtern. Mehrere Suchwörter
müssen gemeinsam vorkommen; Großschreibung und Akzente werden ignoriert.
News-/Devlog-Filter, Trefferanzeige, Leeren und Zurücksetzen funktionieren ohne
Seitenneuladen oder zusätzliche Bibliotheken. `q` und `type` in der URL erhalten
die Auswahl beim Teilen und Neuladen. Ohne JavaScript bleiben alle Beiträge lesbar.

### Stories auf der Startseite und vollständige Beiträge

**Fresh from development / Neu aus der Entwicklung** ist das native
`djangocms-stories`-Plugin **Latest entries** (`BlogLatestEntriesPlugin`) im
Platzhalter `latest`. Im CMS können Anzahl (standardmäßig drei), App-Konfiguration,
Tags und Kategorien eingestellt werden. Das Template
`djangocms_stories/plugins/latest_entries.html` übernimmt das F2-Orbit-Design und
verwendet ausschließlich die Beiträge, die das Stories-Plugin liefert.

Bestehende Startseiten einmal überführen:

```bash
docker compose -f docker-compose.local.yml exec django python manage.py install_home_stories --username DEIN_ADMIN
```

Neue Startseiten erhalten das Plugin automatisch. Der Installer ergänzt auch
den neuen Platzhalter und schützt bearbeitete Entwürfe. Vorhandene native
Stories-Einstellungen und ihre Tag-/Kategoriebeziehungen bleiben beim Kopieren
und Veröffentlichen von Seitenversionen erhalten.

Der redaktionelle Datensatz enthält **fünf Devlogs und fünf News**, jeweils in
Deutsch und Englisch mit Einleitung, vier Abschnitten, Metabeschreibung,
Autor, Kategorie und Titelbild. Die vorhandenen fünf Kurzvorlagen werden zu
vollständigen Beiträgen erweitert; fünf weitere Beiträge kommen hinzu.

```bash
docker compose -f docker-compose.local.yml exec django python manage.py seed_stories --username DEIN_ADMIN
```

Die Bilder werden aus den vorhandenen Spielmotiven in django-filer importiert
und direkt am Stories-Beitrag referenziert. Karten verwenden 768×432-Thumbnails.
Die Texte liegen in `space_game/theme/story_content.json`. Der Befehl ist
wiederholbar, verwendet vorhandene Medien erneut und bewahrt nach der ersten
Übernahme spätere redaktionelle Änderungen. Geänderte unveröffentlichte
Beitragsentwürfe werden vor dem ersten Import geschützt. Bearbeitet werden die
Inhalte anschließend über **Stories → Posts** im Admin.

Für die Bild-Metadaten verwendet django-meta die Domain der aktuellen Django-Site
und `META_SITE_PROTOCOL` (Standard `https`). Damit funktionieren bebilderte
Beitragsseiten auch unter Uvicorn ohne threadlokales Request-Objekt.

### Admin: Mission Control

Der Django-Admin unter `/admin/` verwendet das Space-Game-Design mit lokalem
JetBrains Mono, dunklen Oberflächen und cyanfarbenen Akzenten. Das Dashboard
verlinkt auf Seiten, Stories, Medien und Cookie-Einstellungen, soweit der
angemeldete Benutzer die jeweiligen Berechtigungen besitzt. Djangos Hell-/Dunkel-
Umschalter und die Sidebar-Suche bleiben verfügbar; beim ersten Besuch wird
das dunkle Theme gewählt.

Die Anpassung liegt in `space_game/templates/admin/`,
`space_game/static/scss/admin.scss` und `space_game/theme/admin.py`. Der vorhandene
`npm run build`-/`npm run watch`-Ablauf erzeugt zusätzlich `build/admin.css`.
Website und Admin teilen nur die lokalen Fontdateien; Bootstrap wird nicht in
die Admin-Oberfläche importiert. Django-CMS-Seitenbaum und Filer verwenden
dieselbe Farbpalette. Die nativen Admin-Formulare, Berechtigungen und Aktionen
bleiben die Grundlage.

Die django-CMS-Toolbar und die Strukturansicht der vorhandenen Plugins verwenden
ebenfalls das Mission-Control-Design. Das gilt auch für verschachtelte Karten,
Plugin-Suche, Kontextmenüs und Dialograhmen. Deren Styles liegen separat in
`space_game/static/scss/cms-editor.scss` und werden als `build/cms-editor.css`
über `space_game/theme/cms_toolbars.py` eingebunden, sobald die CMS-Toolbar
angezeigt wird. Auch die eigenständige Strukturansicht erhält dadurch das Theme.
Der native Farbumschalter übernimmt dieselbe gespeicherte Hell-/Dunkel-Auswahl
wie der Admin; ohne gespeicherte Auswahl startet der Editor dunkel.
Das Logo wird in `space_game/templates/cms/toolbar/items/logo.html` angepasst.
Die öffentlichen Seiten laden das Editor-Stylesheet ohne Toolbar nicht.

Das Projekt verwendet django CMS **5.1.3** mit Django 6.0.10 und Python 3.14.
Die CMS-Pakete sind in `pyproject.toml` und `uv.lock` festgehalten:

| Paket | Version |
| --- | --- |
| django-cms | 5.1.3 |
| djangocms-transfer | 2.0.1 |
| djangocms-stories | 0.9.3 |
| djangocms-frontend | 2.5.3 |
| djangocms-cookie-love | 0.1.1 |
| djangocms-text | 1.0.2 |
| djangocms-versioning | 2.8.0 |

### Bootstrap-Theme und SCSS

Das Space-Game-Theme basiert auf den Bildern und der Look-Beschreibung aus
`space-game-pack.zip`: Hintergrund `#040A0E`, Akzent `#8BE0EC`, Warnfarbe `#FFAB26`
und lokal ausgelieferte JetBrains Mono. Die ZIP enthielt kein fertiges HTML-/SCSS-Theme.
Der Launcher-Screenshot wird entsprechend der beiliegenden LIESMICH nicht ausgeliefert.

Bootstrap **5.3.8** und die Schrift werden über npm installiert. Node.js **24**
verwenden (siehe `.nvmrc`). Für Entwicklung ohne Docker vor dem Django-Start:

```bash
npm ci
npm run build
```

`npm run watch` baut das CSS bei SCSS-Änderungen neu. Unter Windows bei gesperrten
PowerShell-Skripten `npm.cmd` anstelle von `npm` verwenden.
`space_game/static/scss/project.scss` enthält die Bootstrap-Variablen und importiert
die Bootstrap-SCSS-Quellen; `_orbit.scss` enthält das aktuelle F2-Orbit-Layout,
`_fonts.scss` die lokalen Fonts. `_theme.scss` ist die frühere Theme-Referenz.
Der Build schreibt CSS, Bootstrap-JavaScript, Fonts und Lizenzen nach
`space_game/static/build/`. Dieses Verzeichnis und `node_modules/` sind gitignored;
`package.json`, `package-lock.json`, SCSS und Bildquellen werden versioniert.
Es werden keine Bootstrap- oder Font-CDNs eingebunden.

Das lokale Docker-Image enthält Node/npm. Beim Start werden Abhängigkeiten und
Assets aufgebaut und der SCSS-Watcher gestartet. Ein separates Volume hält die
Linux-`node_modules` vom Host getrennt. Der Produktionsbuild erzeugt die Assets in
einer eigenen Node-Buildstufe; im Laufzeitimage wird Node nicht benötigt. CI baut
die Assets ebenfalls vor den Django-Tests.

Die neue CMS-Vorlage **Space Game — Landingpage** enthält Hero, drei Motivkarten,
Community-Bereich und Galerie mit überschreibbaren CMS-Platzhaltern. Neue
Bootstrap-Startseiten verwenden diese Vorlage automatisch. Bei einer bestehenden
Startseite die Vorlage in den CMS-Seiteneinstellungen auswählen und veröffentlichen;
vorhandene Inhalte bleiben erhalten. Die weiteren Aufnahmen liegen unter
`space_game/static/images/theme/fotoshooting/`.

Der Hero ist eine eigene `CMSFrontendComponent` von **djangocms-frontend** und
liegt unter **Space Game → Space Game Hero** im Plugin-Menü. Im Platzhalter `hero`
lassen sich Hintergrundbild (django-filer), Bildbeschreibung, Vorspann,
Überschrift, Beschreibung und zwei optionale Buttons bearbeiten. Die Linkauswahl
unterstützt CMS-Seiten, externe URLs, Dateien und Anker. Ohne ausgewähltes Bild
wird das ursprüngliche Space-Game-Motiv verwendet. Texte werden als Klartext
ausgegeben. Neue Startseiten erhalten automatisch eine gespeicherte Hero-Instanz.

Für bereits bestehende Startseiten nach `migrate` einmal ausführen:

```bash
docker compose -f docker-compose.local.yml exec django python manage.py install_home_hero --username DEIN_ADMIN
```

Der Befehl erzeugt eine neue veröffentlichte Version und lässt vorhandene Hero-
Plugins unverändert. Gibt es bereits einen unveröffentlichten Seitenentwurf,
den Hero dort über das CMS hinzufügen und den Entwurf regulär veröffentlichen.
Die Komponente ist in `space_game/theme/cms_components.py` definiert; ihr Template
liegt in `space_game/templates/theme/components/hero.html`.

### Kartenmodul unter dem Hero

Der Platzhalter `discovery` enthält **Space Game → Space Game Cards**. Überschrift
und Vorspann werden am Modul bearbeitet. Darunter lassen sich einzelne
**Space Game Card**-Plugins hinzufügen, bearbeiten, umsortieren und entfernen.
Eine Karte enthält Titel, Text, Vorspann, Bild samt Alternativtext und einen
optionalen Link. Bilder kommen aus django-filer; alternativ sind die drei Motive
des ursprünglichen Bereichs auswählbar.

Besucher sehen zunächst maximal sechs Karten. Ab der siebten Karte erscheint
**alle laden** und blendet die restlichen Karten desselben Moduls ein. Der Button
verschwindet anschließend. Ohne JavaScript und im CMS-Bearbeitungsmodus bleiben
alle Karten sichtbar. Die Karten werden responsiv in einer, zwei oder drei
Spalten angezeigt.

Neue Startseiten erhalten automatisch die bisherigen drei Karten als gespeicherte
Plugins. Bestehende Startseiten nach `migrate` einmal überführen:

```bash
docker compose -f docker-compose.local.yml exec django python manage.py install_home_cards --username DEIN_ADMIN
```

Vorhandene Plugins und geänderte Entwürfe bleiben erhalten. Ein unveränderter
Frontend-Entwurf kann für die Übernahme verwendet werden; bei eigenen Änderungen
das Modul im bestehenden Entwurf ergänzen und regulär veröffentlichen.

### Call to Action unter den Karten

Im Platzhalter `community` liegt **Space Game → Space Game CTA**, ebenfalls eine
`CMSFrontendComponent` von **djangocms-frontend**. Vorspann, Überschrift,
Beschreibung, Button-Text und Button-Ziel lassen sich im CMS bearbeiten. Der
Button unterstützt CMS-Seiten, externe URLs, Dateien und Anker. Das responsive
Space-Game-Layout bleibt erhalten; entfernte CTA-Plugins werden nicht durch
fest eingebauten Inhalt ersetzt.

Neue Startseiten erhalten den CTA automatisch. Bestehende Startseiten nach
`migrate` einmal überführen:

```bash
docker compose -f docker-compose.local.yml exec django python manage.py install_home_cta --username DEIN_ADMIN
```

Vorhandene Inhalte und geänderte Entwürfe bleiben erhalten. Bei einem eigenen
Entwurf den CTA dort ergänzen und regulär veröffentlichen. Die Komponente liegt
in `space_game/theme/cms_components.py`, ihr Template in
`space_game/templates/theme/components/cta.html`.

### Galerie unter dem CTA

Im Platzhalter `gallery` liegt **Space Game → Space Game Gallery** mit beliebig
vielen **Space Game Gallery Image**-Plugins als Kindern. Am Modul werden Vorspann,
Überschrift und Beschreibung bearbeitet. Pro Bild stehen django-filer, ein
Alternativtext und eine optionale Caption zur Verfügung; die beiden bisherigen
Motive lassen sich auch ohne Medienimport als Standardbild auswählen. Bilder
können im CMS hinzugefügt, umsortiert und entfernt werden.

Der Slider kombiniert eine gleitende Bewegung mit sanftem Zoom und eingeblendeten
Captions. Links steht das große Bild, rechts eine senkrechte Vorschauleiste.
Beide Bereiche blenden ihre Scrollleisten aus; Touch-Scrolling bleibt möglich.
Vor-/Zurück-Pfeile und der Vollbild-Button liegen direkt im großen Bild. Der
Vollbildmodus enthält auch die Vorschauen und lässt sich über den Schließen-
Button oder Escape verlassen. Ohne Browser-Vollbild-Unterstützung öffnet sich
stattdessen eine bildschirmfüllende Dialogansicht.
Die Tastatursteuerung unterstützt Pfeil links/rechts sowie Pos1/Ende.
Es gibt keinen automatischen Bildwechsel. Die Systemeinstellung für reduzierte
Bewegung schaltet Animationen und weiches Scrollen ab. Bei nur einem Bild sind
die Navigationspfeile und Vorschauen ausgeblendet; Vollbild bleibt verfügbar.
Ohne JavaScript bleibt die Galerie horizontal
scrollbar; im CMS-Bearbeitungsmodus stehen alle Bilder untereinander, damit sie
direkt bearbeitet werden können. Mehrere Galerien funktionieren unabhängig.

Neue Startseiten erhalten automatisch die zwei bisherigen Motive als Plugins.
Bestehende Startseiten nach `migrate` einmal überführen:

```bash
docker compose -f docker-compose.local.yml exec django python manage.py install_home_gallery --username DEIN_ADMIN
```

Vorhandene Galerie-Inhalte und geänderte Entwürfe bleiben erhalten. Bei einem
eigenen Entwurf die Galerie dort ergänzen und regulär veröffentlichen. Templates
liegen in `space_game/templates/theme/components/gallery*.html`, Styles in
`space_game/static/scss/_gallery.scss` und die Steuerung in
`space_game/static/js/project.js`. Der vorhandene npm-Build erstellt das CSS.

### Start mit Docker

Die vorhandenen lokalen Umgebungsdateien unter `.envs/.local/` werden weiter
verwendet. Anschließend:

```bash
docker compose -f docker-compose.local.yml build django
docker compose -f docker-compose.local.yml run --rm django python manage.py migrate
docker compose -f docker-compose.local.yml run --rm django python manage.py createsuperuser
docker compose -f docker-compose.local.yml run --rm django python manage.py bootstrap_cms --username DEIN_ADMIN
docker compose -f docker-compose.local.yml up
```

Unter `http://localhost:8000/admin/` anmelden. Der Bootstrap-Befehl erstellt und
veröffentlicht `/`, `/about/` und `/stories/`, inklusive Stories-Konfiguration und
Apphook. Er benötigt einen bestehenden aktiven Superuser und lässt vorhandene
Seiten mit diesen CMS-IDs sowie eine vorhandene Startseite unverändert.
Es werden keine Benutzer oder Passwörter automatisch angelegt.

Die bisherigen statischen Home-/About-Views werden durch CMS-Seiten ersetzt.
Seiteninhalte lassen sich über die CMS-Toolbar mit Text- und Bootstrap-5-Plugins
bearbeiten. Änderungen werden zunächst als Entwurf gespeichert und müssen
veröffentlicht werden. Stories werden im Admin angelegt und veröffentlicht;
Transfer steht im CMS für den Import/Export von Plugin-Inhalten bereit.
Benutzerverwaltung, Allauth, API und Celery sind weiterhin verfügbar.
Englisch bleibt Standardsprache; deutsche Seitenübersetzungen können im CMS
hinzugefügt werden. Beide Sprachen nutzen dieselben URL-Pfade ohne Sprachpräfix.

### Cookie Love

Im Admin unter **Cookie consent configs** eine aktive Konfiguration und die
benötigten Cookie-Gruppen/Cookies anlegen. Erst dann erscheint das Banner.
Das Banner wird zentral im Basistemplate eingebunden; keinen zusätzlichen
Banner-Plugin auf Seiten einsetzen. Die Cookie-Einstellungen lassen sich im
Footer erneut öffnen. Datenschutz- und Impressumslinks in der Konfiguration
eintragen. Optionale Skripte müssen explizit blockiert eingebunden werden:

```html
<script type="text/plain" data-cookie-group="analytics">
  // Erst nach Einwilligung ausführen.
</script>
```

In Produktion kann `COOKIE_LOVE_IP_SALT` separat gesetzt werden; andernfalls
wird `DJANGO_SECRET_KEY` verwendet. Consent-Cookies sind in Produktion nur über
HTTPS verfügbar, lokal ist HTTP erlaubt. Zur Aufbewahrungsfrist regelmäßig
`python manage.py purge_old_consents` ausführen.

### Migrationen und Prüfung

Die vollständige Datenbank vor einem bestehenden Deployment sichern und dann
`migrate` ausführen. `bootstrap_cms` ist ein separater, optionaler Einrichtungsschritt.
Die Migrationen in `space_game/contrib/stories/migrations/` übernehmen die drei
Upstream-Migrationen und ergänzen den in Stories 0.9.3 fehlenden Modellstand,
einschließlich der aktuellen Parler-Constraints. Bei einem Stories-Upgrade diese
Ergänzung mit den neuen Upstream-Migrationen abgleichen.

```bash
uv sync --frozen
uv run python manage.py check
uv run python manage.py cms check
uv run python manage.py makemigrations --check --dry-run
uv run pytest
```

Für lokale Ausführung ohne Docker die PostgreSQL-Verbindung über `DATABASE_URL`
setzen, `USE_DOCKER=no` und `DJANGO_SETTINGS_MODULE=config.settings.local` verwenden.
Unter Windows wird der binäre Psycopg-Treiber installiert; Docker/Linux verwendet
weiterhin die C-Erweiterung.

[![Built with Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg?logo=cookiecutter)](https://github.com/cookiecutter/cookiecutter-django/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

## Settings

Moved to [settings](https://cookiecutter-django.readthedocs.io/en/latest/1-getting-started/settings.html).

## Basic Commands

### Setting Up Your Users

- To create a **normal user account**, just go to Sign Up and fill out the form. Once you submit it, you'll see a "Verify Your E-mail Address" page. Go to your console to see a simulated email verification message. Copy the link into your browser. Now the user's email should be verified and ready to go.

- To create a **superuser account**, use this command:

      uv run python manage.py createsuperuser

For convenience, you can keep your normal user logged in on Chrome and your superuser logged in on Firefox (or similar), so that you can see how the site behaves for both kinds of users.

### Type checks

Running type checks with mypy:

    uv run mypy space_game

### Test coverage

To run the tests, check your test coverage, and generate an HTML coverage report:

    uv run coverage run -m pytest
    uv run coverage html
    uv run open htmlcov/index.html

#### Running tests with pytest

    uv run pytest

### Live reloading and Sass CSS compilation

Use `npm run watch` for SCSS changes; see [Bootstrap-Theme und SCSS](#bootstrap-theme-und-scss).
The local Docker start command runs the watcher automatically.

### Celery

This app comes with Celery.

To run a celery worker:

```bash
cd space_game
uv run celery -A config.celery_app worker -l info
```

Please note: For Celery's import magic to work, it is important _where_ the celery commands are run. If you are in the same folder with _manage.py_, you should be right.

To run [periodic tasks](https://docs.celeryq.dev/en/stable/userguide/periodic-tasks.html), you'll need to start the celery beat scheduler service. You can start it as a standalone process:

```bash
cd space_game
uv run celery -A config.celery_app beat
```

or you can embed the beat service inside a worker with the `-B` option (not recommended for production use):

```bash
cd space_game
uv run celery -A config.celery_app worker -B -l info
```

### Email Server

In development, it is often nice to be able to see emails that are being sent from your application. For that reason local SMTP server [Mailpit](https://github.com/axllent/mailpit) with a web interface is available as docker container.

Container mailpit will start automatically when you will run all docker containers.
Please check [cookiecutter-django Docker documentation](https://cookiecutter-django.readthedocs.io/en/latest/2-local-development/developing-locally-docker.html) for more details how to start all containers.

With Mailpit running, to view messages that are sent by your application, open your browser and go to `http://127.0.0.1:8025`

### Sentry

Sentry is an error logging aggregator service. You can sign up for a free account at <https://sentry.io/signup/?code=cookiecutter> or download and host it yourself.
The system is set up with reasonable defaults, including 404 logging and integration with the WSGI application.

You must set the DSN url in production.

## Deployment

### MCP mit Claude und verpflichtende Admin-2FA

Der ASGI-Server stellt unter `http://localhost:8000/mcp` einen Streamable-HTTP-MCP
bereit. Nach Änderungen an den Python-Abhängigkeiten lokal einmal ausführen:

```powershell
docker compose -f docker-compose.local.yml build django
docker compose -f docker-compose.local.yml up -d django
```

Die Anmeldung verwendet den vorhandenen Django-Admin-Benutzer. Beim ersten Login
unter `/admin/` muss jeder aktive Staff-Benutzer den QR-Code mit einer
Authenticator-App scannen und einen gültigen TOTP-Code eingeben. Anschließend die
einmal angezeigten Wiederherstellungscodes sichern. Bestehende Sitzungen ohne
2FA-Nachweis werden ebenfalls zur Einrichtung bzw. zweiten Prüfung geleitet.
Staff-Passwörter und die bisherigen DRF-API-Tokens allein erlauben keinen
Verwaltungszugriff mehr. Normale Spieler-Accounts behalten ihre Anmeldung.

**Claude Code:** Die eingecheckte `.mcp.json` enthält bereits den lokalen Endpunkt.
Das Projekt in Claude Code öffnen, den Projektserver aktivieren und unter `/mcp`
für `space-game` die Browser-Anmeldung starten. Alternativ ohne Projektdatei:

```powershell
claude mcp add --transport http space-game http://localhost:8000/mcp
```

**Claude Desktop unter Windows:** Den Eintrag aus
[`config/mcp/claude_desktop_config.windows.example.json`](config/mcp/claude_desktop_config.windows.example.json)
in `%APPDATA%\Claude\claude_desktop_config.json` übernehmen und Claude vollständig
neu starten. Vorhandene `mcpServers`-Einträge beibehalten. Node.js 24/npm müssen
verfügbar sein. Die fest versionierte `mcp-remote`-Bridge läuft auf deinem Rechner
und öffnet bei Bedarf die Anmeldung im Browser. Ein Cloud-Connector kann den
lokalen `localhost`-Server nicht erreichen.

Beide Clients verwenden OAuth mit PKCE, dynamischer Client-Registrierung und
Zustimmung im Browser nach der 2FA-Prüfung. In den JSON-Dateien stehen keine
Passwörter oder Tokens. Die Zustimmung umfasst `mcp:read`, `mcp:write` und
`mcp:publish`; zusätzlich gelten bei jedem Aufruf die aktuellen Django- und
CMS-Berechtigungen des Benutzers. Nur Lesezugriff lässt sich durch die angefragten
Scopes begrenzen. Access-Tokens gelten eine Stunde; Refresh-Tokens rotieren und
werden spätestens nach sieben Tagen ungültig. Passwortänderung, Staff-Entzug,
Deaktivierung oder Zurücksetzen des TOTP-Faktors widerrufen die Tokens.

Verfügbare Werkzeuge:

| Werkzeuge | Verwaltung |
| --- | --- |
| `whoami`, `management_catalog` | Benutzer, Scopes und verfügbare Admin-Modelle |
| `records_read`, `records_write` | Admin-Formularschema und CRUD, einschließlich Gruppen und Einstellungen; Benutzeränderungen nur für Superuser |
| `pages_read`, `pages_write` | CMS-Seiten anlegen, lesen, als Entwurf bearbeiten, übersetzen und löschen |
| `plugins_read`, `plugins_write` | Plugin-Typen mit Formularfeldern, Platzhalter, Plugin-Baum und Konfiguration; hinzufügen, bearbeiten, verschieben und löschen |
| `stories_read`, `stories_write` | News/Devlogs, Übersetzungen und Artikel-Metadaten wie Titelbild, Kategorien und Tags |
| `content_versions` | Entwurf erstellen, veröffentlichen, zurückziehen, archivieren und verwerfen |
| `media_read`, `media_write`, `media_upload` | Filer-Bilder/Dateien, Metadaten, Upload und Löschen |

Seiten- und Artikeltexte werden als Entwurf bearbeitet. Vor Plugin-Änderungen mit
`content_versions(action="draft", ...)` den Entwurf bestimmen, danach dessen
Plugin-IDs mit `plugins_read(action="list", content_id=...)` lesen. Die
Formularfelder zuerst mit `plugins_read(action="types")` prüfen. Veröffentlichen
und das Löschen ganzer Seiten/Artikel erfordern zusätzlich `mcp:publish`.
Artikel-Metadaten (`stories_write`, Aktion `metadata`) gelten wie im nativen Admin
für alle Sprachfassungen und Versionen sofort und benötigen ebenfalls diesen
Scope. Sicherheitsdaten wie Passwort-Hashes, OAuth-Tokens und TOTP-Schlüssel sind
vom MCP-Lesezugriff ausgeschlossen. Änderungen erscheinen unter **Control →
Audit events** im Admin; dort werden keine Inhaltsdaten oder Geheimnisse geloggt.

Uploads: `media_upload(action="begin", filename=..., size=..., kind="image"|"file")`
starten, anschließend Base64-Blöcke mit höchstens 1 MiB Rohdaten und passendem
`offset` über `chunk` senden, mit `finish` abschließen. `status`/`list` zeigen die
eigenen laufenden Uploads; `abort` verwirft sie. Optional einen SHA-256-Hash beim
Start angeben. Das Limit beträgt standardmäßig 512 MiB. Der Abschluss prüft Bilder
und die nativen Filer-Dateiregeln. Die zurückgegebene `reference`, z. B.
`{"model": "filer.image", "pk": 42}`, kann einem Plugin-Feld wie `image` oder
`launcher_file` zugewiesen werden. Neue Assets sind öffentlich abrufbar.

Für den Produktivbetrieb `MCP_BASE_URL=https://deine-domain.example` setzen und
denselben Ursprung in den Client-Dateien verwenden. Die URL muss dem von außen
erreichbaren Ursprung entsprechen; MCP prüft Host, Origin und Token-Zieladresse.
Der vorhandene Produktionsstart verwendet bereits Gunicorn mit ASGI/Uvicorn.
`DJANGO_SECRET_KEY` und bisherige Schlüssel in `SECRET_KEY_FALLBACKS` sicher
aufbewahren: Sie schützen auch die verschlüsselten 2FA-Geheimnisse. Das Staging
unter `.mcp_uploads/` wird nicht eingecheckt. Regelmäßig serverseitig bereinigen:

```bash
python manage.py cleanup_mcp_uploads
python manage.py cleartokens
```

Bei verlorenem zweiten Faktor zuerst einen Wiederherstellungscode nutzen. Nur
mit Serverzugriff kann die Einrichtung erzwungen zurückgesetzt werden:

```bash
python manage.py reset_staff_mfa --username ADMINNAME
```

Das beendet alle Sitzungen und widerruft alle MCP-Tokens dieses Benutzers; beim
nächsten Login ist eine neue 2FA-Einrichtung erforderlich.

Protokoll- und Client-Dokumentation: [Claude Code MCP](https://code.claude.com/docs/en/mcp),
[mcp-remote](https://github.com/punkpeye/mcp-remote),
[Django OAuth Toolkit](https://django-oauth-toolkit.readthedocs.io/en/stable/),
[django-allauth MFA](https://docs.allauth.org/en/latest/mfa/).

The following details how to deploy this application.

### Docker

See detailed [cookiecutter-django Docker documentation](https://cookiecutter-django.readthedocs.io/en/latest/3-deployment/deployment-with-docker.html).
