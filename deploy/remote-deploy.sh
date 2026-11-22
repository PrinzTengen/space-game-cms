#!/usr/bin/env bash
# Runs ON THE SERVER. Called by deploy/deploy.ps1 — not meant to be run by hand.
#
# Expects in $STAGE_DIR (default: directory of this script):
#   bundle.tar.gz   code + .envs/.production/*
#   db.dump         (optional) pg_dump -Fc of the local database
#   media.tar.gz    (optional) contents of space_game/media
#
# Env: APP_DIR, APP_PORT, SITE_DOMAIN

set -o errexit
set -o pipefail
set -o nounset

if [ "$(id -u)" -ne 0 ]; then
  exec sudo --preserve-env=APP_DIR,APP_PORT,SITE_DOMAIN,STAGE_DIR bash "$0" "$@"
fi

STAGE_DIR="${STAGE_DIR:-$(cd "$(dirname "$0")" && pwd)}"
APP_DIR="${APP_DIR:-/opt/space_game}"
APP_PORT="${APP_PORT:-8080}"
SITE_DOMAIN="${SITE_DOMAIN:-}"

step() { printf '\n\033[1;36m==> %s\033[0m\n' "$*"; }
fail() { printf '\n\033[1;31mFEHLER: %s\033[0m\n' "$*" >&2; exit 1; }

case "$APP_DIR" in
  /|/root|/home|/usr|/etc|/var|/opt|"") fail "Unsicheres APP_DIR: '$APP_DIR'" ;;
esac
[ -f "$STAGE_DIR/bundle.tar.gz" ] || fail "bundle.tar.gz fehlt in $STAGE_DIR"

# --- Docker ------------------------------------------------------------------
if ! command -v curl >/dev/null 2>&1; then
  apt-get update -y && apt-get install -y curl
fi
if ! command -v docker >/dev/null 2>&1; then
  step "Docker ist nicht installiert – installiere Docker Engine"
  curl -fsSL https://get.docker.com | sh
  systemctl enable --now docker
fi
docker compose version >/dev/null 2>&1 || fail "'docker compose' (Plugin v2) fehlt auf dem Server"

# --- Code --------------------------------------------------------------------
step "Entpacke Code nach $APP_DIR"
mkdir -p "$APP_DIR"
# Code is replaced completely; database and media live in Docker volumes.
find "$APP_DIR" -mindepth 1 -maxdepth 1 -exec rm -rf {} +
tar -xzf "$STAGE_DIR/bundle.tar.gz" -C "$APP_DIR"
chmod 600 "$APP_DIR"/.envs/.production/.django "$APP_DIR"/.envs/.production/.postgres
cd "$APP_DIR"

export APP_PORT
COMPOSE=(docker compose -p space_game -f docker-compose.production.yml -f docker-compose.ip.yml)

step "Baue Images (dauert beim ersten Mal einige Minuten)"
"${COMPOSE[@]}" build

step "Starte PostgreSQL und Redis"
"${COMPOSE[@]}" up -d postgres redis
for i in $(seq 1 60); do
  if "${COMPOSE[@]}" exec -T postgres sh -c 'pg_isready -q -U "$POSTGRES_USER" -d "$POSTGRES_DB"'; then
    break
  fi
  [ "$i" -eq 60 ] && fail "PostgreSQL wird nicht bereit"
  sleep 2
done

# --- Database restore --------------------------------------------------------
if [ -f "$STAGE_DIR/db.dump" ]; then
  step "Stoppe App-Container für den Datenbank-Import"
  "${COMPOSE[@]}" stop django celeryworker celerybeat nginx 2>/dev/null || true

  tables=$("${COMPOSE[@]}" exec -T postgres sh -c \
    'psql -tAq -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "select count(*) from information_schema.tables where table_schema = '\''public'\''"')
  if [ "${tables//[[:space:]]/}" != "0" ]; then
    step "Sichere bestehende Prod-Datenbank (Volume production_postgres_data_backups)"
    "${COMPOSE[@]}" exec -T postgres backup
  fi

  step "Spiele lokales Datenbank-Backup ein"
  "${COMPOSE[@]}" exec -T postgres sh -c \
    'dropdb -U "$POSTGRES_USER" --if-exists --force "$POSTGRES_DB" && createdb -U "$POSTGRES_USER" "$POSTGRES_DB"'
  "${COMPOSE[@]}" exec -T postgres sh -c \
    'pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" --no-owner --no-acl --exit-on-error' \
    < "$STAGE_DIR/db.dump"
fi

# --- Media -------------------------------------------------------------------
if [ -f "$STAGE_DIR/media.tar.gz" ]; then
  step "Kopiere Media-Dateien (Uploads) ins Volume"
  "${COMPOSE[@]}" run --rm --no-deps -T --entrypoint sh django -c \
    'find /app/space_game/media -mindepth 1 -delete && tar -xzf - -C /app/space_game/media' \
    < "$STAGE_DIR/media.tar.gz"
fi

# --- Migrations & start ------------------------------------------------------
step "Führe Migrationen aus"
"${COMPOSE[@]}" run --rm django python manage.py migrate --noinput

if [ -f "$STAGE_DIR/mfa_old_key" ]; then
  step "Schlüssele MFA-Secrets auf den Prod-SECRET_KEY um"
  MFA_OLD_SECRET_KEY="$(cat "$STAGE_DIR/mfa_old_key")"
  export MFA_OLD_SECRET_KEY
  rm -f "$STAGE_DIR/mfa_old_key"
  "${COMPOSE[@]}" run --rm -e MFA_OLD_SECRET_KEY django python manage.py reencrypt_mfa_secrets
  unset MFA_OLD_SECRET_KEY
fi

if [ -n "$SITE_DOMAIN" ]; then
  "${COMPOSE[@]}" run --rm django python manage.py shell -c \
    "from django.contrib.sites.models import Site; Site.objects.update_or_create(id=1, defaults={'domain': '$SITE_DOMAIN', 'name': 'Space Game'})"
fi

step "Starte alle Dienste"
"${COMPOSE[@]}" up -d --remove-orphans

if command -v ufw >/dev/null 2>&1 && ufw status | grep -q "Status: active"; then
  step "Öffne Port $APP_PORT in der Firewall (ufw)"
  ufw allow "$APP_PORT/tcp" >/dev/null
fi

step "Warte auf die App"
ok=0
for i in $(seq 1 60); do
  code=$(curl -s -o /dev/null -w '%{http_code}' "http://127.0.0.1:$APP_PORT/" || true)
  if [ -n "$code" ] && [ "$code" != "000" ] && [ "$code" != "502" ] && [ "$code" != "504" ]; then
    ok=1; break
  fi
  sleep 3
done

docker image prune -f >/dev/null 2>&1 || true
rm -rf "$STAGE_DIR"

if [ "$ok" -eq 1 ]; then
  printf '\n\033[1;32mApp antwortet (HTTP %s).\033[0m\n' "$code"
else
  "${COMPOSE[@]}" ps
  "${COMPOSE[@]}" logs --tail 60 django
  fail "App antwortet nicht auf Port $APP_PORT – siehe Logs oben"
fi
