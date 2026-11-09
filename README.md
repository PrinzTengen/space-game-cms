# Space Game

website

## django CMS

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
die Bootstrap-SCSS-Quellen; `_theme.scss` enthält das Layout und die lokalen Fonts.
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
liegt in `space_game/templates/theme/components/hero.html`. Community und Galerie
verwenden weiterhin die bestehenden Template-Vorgaben.

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

The following details how to deploy this application.

### Docker

See detailed [cookiecutter-django Docker documentation](https://cookiecutter-django.readthedocs.io/en/latest/3-deployment/deployment-with-docker.html).
