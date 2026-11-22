<#
.SYNOPSIS
  Deployt Space Game auf einen Linux-Server (Docker) und macht es unter http://<IP>:<Port> erreichbar.

.DESCRIPTION
  1. Erzeugt/aktualisiert .envs/.production/.django + .postgres mit sicheren Zufalls-Secrets
     (bestehende echte Secrets bleiben erhalten, Platzhalter wie "debug" werden ersetzt).
  2. Erstellt ein Backup der lokalen Datenbank (Docker-Container space_game_local_postgres)
     und packt space_game/media (Uploads) ein.
  3. Packt den Code (alles was git kennt, inkl. ungetrackter, nicht ignorierter Dateien).
  4. Lädt alles per scp hoch, baut auf dem Server die Images, spielt DB + Media ein,
     migriert und startet die Container.

.EXAMPLE
  .\deploy\deploy.ps1 -Server root@203.0.113.10
.EXAMPLE
  .\deploy\deploy.ps1 -Server deploy@203.0.113.10 -Port 8080 -SshKey ~\.ssh\id_ed25519
.EXAMPLE
  # Nur Code aktualisieren, Prod-Datenbank und Media unangetastet lassen
  .\deploy\deploy.ps1 -Server root@203.0.113.10 -NoData
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$Server,     # user@host
    [int]$Port = 8080,                                   # öffentlicher HTTP-Port auf dem Server
    [string]$RemoteDir = "/opt/space_game",
    [string]$SshKey = "",
    [int]$SshPort = 22,
    [switch]$NoData,                                     # kein DB-/Media-Sync
    [switch]$Yes,                                        # keine Rückfragen
    # Mailgun SMTP (Mailgun -> Sending -> Domain settings -> SMTP credentials).
    # Leer lassen = später; Mails landen dann nur im Log.
    [string]$MailgunUser = "",
    [string]$MailgunPassword = "",
    [ValidateSet("eu", "us")][string]$MailgunRegion = "eu"
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version 2

$Root = Split-Path -Parent $PSScriptRoot
$EnvDir = Join-Path $Root ".envs\.production"
$DjangoEnvFile = Join-Path $EnvDir ".django"
$PostgresEnvFile = Join-Path $EnvDir ".postgres"
$Stage = Join-Path ([IO.Path]::GetTempPath()) ("space_game_deploy_" + [guid]::NewGuid().ToString("N").Substring(0, 8))
$Tar = Join-Path $env:SystemRoot "System32\tar.exe"
$Utf8NoBom = New-Object System.Text.UTF8Encoding($false)

function Write-Step([string]$msg) { Write-Host "`n==> $msg" -ForegroundColor Cyan }

function Invoke-Native {
    param([string]$Exe, [string[]]$Arguments)
    & $Exe @Arguments
    if ($LASTEXITCODE -ne 0) { throw "'$Exe $($Arguments -join ' ')' schlug fehl (Exit $LASTEXITCODE)" }
}

function New-Secret([int]$Length = 50) {
    $chars = "abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789".ToCharArray()
    $rng = [Security.Cryptography.RandomNumberGenerator]::Create()
    $bytes = New-Object byte[] ($Length * 2)
    $rng.GetBytes($bytes)
    $sb = New-Object Text.StringBuilder
    foreach ($b in $bytes) {
        # Rejection sampling: no modulo bias
        if ($b -lt (256 - (256 % $chars.Length))) { [void]$sb.Append($chars[$b % $chars.Length]) }
        if ($sb.Length -ge $Length) { break }
    }
    if ($sb.Length -lt $Length) { return New-Secret $Length }
    return $sb.ToString()
}

function Read-EnvFile([string]$Path) {
    $map = [ordered]@{}
    if (Test-Path $Path) {
        foreach ($line in [IO.File]::ReadAllLines($Path)) {
            if ($line -match '^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=(.*)$') { $map[$Matches[1]] = $Matches[2].Trim() }
        }
    }
    return $map
}

function Write-EnvFile([string]$Path, $Map, [string]$Header) {
    $lines = @("# $Header", "# Generiert von deploy/deploy.ps1 - NICHT committen.", "")
    foreach ($k in $Map.Keys) { $lines += "$k=$($Map[$k])" }
    [IO.File]::WriteAllText($Path, (($lines -join "`n") + "`n"), $Utf8NoBom)
}

function Test-Placeholder([string]$Value) {
    return [string]::IsNullOrWhiteSpace($Value) -or $Value -match '^(debug|change|changeme|!!!)' -or $Value.Length -lt 12
}

function Get-OrNewSecret($Map, [string]$Key, [int]$Length = 50) {
    if ($Map.Contains($Key) -and -not (Test-Placeholder $Map[$Key])) { return $Map[$Key] }
    return New-Secret $Length
}

# --- Vorbedingungen -----------------------------------------------------------
foreach ($tool in @("ssh", "scp", "git", "docker")) {
    if (-not (Get-Command $tool -ErrorAction SilentlyContinue)) { throw "'$tool' wurde nicht gefunden (PATH)." }
}
if (-not (Test-Path $Tar)) { throw "tar.exe nicht gefunden unter $Tar" }
if ($Server -notmatch '@') { throw "-Server bitte als user@host angeben, z.B. root@203.0.113.10" }
$HostName = $Server.Split("@")[-1]
$PublicUrl = "http://${HostName}:$Port"

$SshOpts = @("-o", "StrictHostKeyChecking=accept-new", "-o", "ServerAliveInterval=30")
if ($SshKey) { $SshOpts += @("-i", (Resolve-Path $SshKey).Path) }
$SshArgs = $SshOpts + @("-p", "$SshPort")
$ScpArgs = $SshOpts + @("-P", "$SshPort")

Write-Step "Prüfe SSH-Verbindung zu $Server"
Invoke-Native ssh ($SshArgs + @($Server, "echo verbunden: `$(uname -sr)"))

# --- 1. Env-Dateien mit Secrets ---------------------------------------------
Write-Step "Erzeuge Produktions-Env mit sicheren Secrets"
New-Item -ItemType Directory -Force $EnvDir | Out-Null
$dj = Read-EnvFile $DjangoEnvFile
$pg = Read-EnvFile $PostgresEnvFile

$pg["POSTGRES_HOST"] = "postgres"
$pg["POSTGRES_PORT"] = "5432"
if (-not $pg.Contains("POSTGRES_DB") -or [string]::IsNullOrWhiteSpace($pg["POSTGRES_DB"])) { $pg["POSTGRES_DB"] = "space_game" }
if (-not $pg.Contains("POSTGRES_USER") -or $pg["POSTGRES_USER"] -match '^(debug|postgres)$' -or [string]::IsNullOrWhiteSpace($pg["POSTGRES_USER"])) {
    $pg["POSTGRES_USER"] = "sg_" + (New-Secret 10).ToLower()
}
$pg["POSTGRES_PASSWORD"] = Get-OrNewSecret $pg "POSTGRES_PASSWORD" 40

# Mailgun: Parameter > bestehender Wert > interaktive Abfrage
$mgUser = $MailgunUser
if (-not $mgUser -and $dj.Contains("EMAIL_HOST_USER")) { $mgUser = $dj["EMAIL_HOST_USER"] }
$mgPass = $MailgunPassword
if (-not $mgPass -and $dj.Contains("EMAIL_HOST_PASSWORD")) { $mgPass = $dj["EMAIL_HOST_PASSWORD"] }
if (-not $mgUser -and -not $Yes) {
    $mgUser = Read-Host "Mailgun SMTP-Benutzer (z.B. postmaster@mg.deinedomain.de) - Enter = später"
}
if ($mgUser -and -not $mgPass) {
    $sec = Read-Host "Mailgun SMTP-Passwort für $mgUser" -AsSecureString
    $mgPass = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($sec))
}

$adminUrl = $null
if ($dj.Contains("DJANGO_ADMIN_URL") -and $dj["DJANGO_ADMIN_URL"] -match '^[A-Za-z0-9]{16,}/$') { $adminUrl = $dj["DJANGO_ADMIN_URL"] }
if (-not $adminUrl) { $adminUrl = (New-Secret 24) + "/" }

$dj["DJANGO_SETTINGS_MODULE"] = "config.settings.production"
$dj["DJANGO_SECRET_KEY"] = Get-OrNewSecret $dj "DJANGO_SECRET_KEY" 64
$dj["DJANGO_ADMIN_URL"] = $adminUrl
$dj["DJANGO_ALLOWED_HOSTS"] = "$HostName,localhost,127.0.0.1"
$dj["DJANGO_CSRF_TRUSTED_ORIGINS"] = $PublicUrl
# Ohne Domain kein TLS -> Cookies/Redirects auf HTTP einstellen
$dj["DJANGO_SECURE_SSL_REDIRECT"] = "False"
$dj["DJANGO_SECURE_COOKIES"] = "False"
$dj["DJANGO_SECURE_HSTS_PRELOAD"] = "False"
$dj["DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS"] = "False"
$dj["COOKIE_LOVE_COOKIE_SECURE"] = "False"
$dj["META_SITE_PROTOCOL"] = "http"
$dj["MCP_BASE_URL"] = $PublicUrl
$dj["REDIS_URL"] = "redis://redis:6379/0"
if (-not $dj.Contains("WEB_CONCURRENCY")) { $dj["WEB_CONCURRENCY"] = "3" }
if (-not $dj.Contains("DJANGO_ACCOUNT_ALLOW_REGISTRATION")) { $dj["DJANGO_ACCOUNT_ALLOW_REGISTRATION"] = "True" }
if (-not $dj.Contains("SENTRY_DSN")) { $dj["SENTRY_DSN"] = "" }
if (-not $dj.Contains("CELERY_FLOWER_USER") -or (Test-Placeholder $dj["CELERY_FLOWER_USER"])) { $dj["CELERY_FLOWER_USER"] = "flower_" + (New-Secret 8).ToLower() }
$dj["CELERY_FLOWER_PASSWORD"] = Get-OrNewSecret $dj "CELERY_FLOWER_PASSWORD" 32
foreach ($k in @("MAILGUN_API_KEY", "MAILGUN_DOMAIN")) { if ($dj.Contains($k) -and -not $dj[$k]) { $dj.Remove($k) } }

if ($mgUser) {
    $mgDomain = $mgUser.Split("@")[-1]
    $smtpHost = "smtp.mailgun.org"
    if ($MailgunRegion -eq "eu") { $smtpHost = "smtp.eu.mailgun.org" }
    $dj["EMAIL_HOST"] = $smtpHost
    $dj["EMAIL_PORT"] = "587"
    $dj["EMAIL_USE_TLS"] = "True"
    $dj["EMAIL_HOST_USER"] = $mgUser
    $dj["EMAIL_HOST_PASSWORD"] = $mgPass
    $dj["DJANGO_DEFAULT_FROM_EMAIL"] = "Space Game <noreply@$mgDomain>"
    $dj["DJANGO_SERVER_EMAIL"] = "Space Game <noreply@$mgDomain>"
} else {
    foreach ($k in @("EMAIL_HOST_USER", "EMAIL_HOST_PASSWORD", "DJANGO_SERVER_EMAIL")) { if ($dj.Contains($k) -and -not $dj[$k]) { $dj.Remove($k) } }
    Write-Host "   Kein Mailgun hinterlegt - E-Mails werden nur in die Container-Logs geschrieben." -ForegroundColor Yellow
}

Write-EnvFile $DjangoEnvFile $dj "Django production"
Write-EnvFile $PostgresEnvFile $pg "PostgreSQL production"
Write-Host "   Gespeichert in $EnvDir (gitignored)."

# --- 2. Lokale Daten sichern -------------------------------------------------
New-Item -ItemType Directory -Force $Stage | Out-Null
try {
    if (-not $NoData) {
        if (-not $Yes) {
            Write-Host "`nACHTUNG: Die Prod-Datenbank und Prod-Media auf $HostName werden durch die LOKALEN Daten ersetzt." -ForegroundColor Yellow
            Write-Host "         (Eine bestehende Prod-DB wird vorher auf dem Server gesichert.)" -ForegroundColor Yellow
            $answer = Read-Host "Fortfahren? (j/N)"
            if ($answer -notmatch '^(j|ja|y|yes)$') { throw "Abgebrochen." }
        }

        Write-Step "Erstelle Backup der lokalen Datenbank"
        $local = Read-EnvFile (Join-Path $Root ".envs\.local\.postgres")
        $container = "space_game_local_postgres"
        $running = (& docker ps --filter "name=^${container}$" --format "{{.Names}}")
        if (-not $running) {
            Write-Host "   Starte lokalen Postgres-Container..."
            Push-Location $Root
            try { Invoke-Native docker @("compose", "-f", "docker-compose.local.yml", "up", "-d", "postgres") } finally { Pop-Location }
            Start-Sleep -Seconds 5
        }
        # Dump im Container schreiben und per docker cp holen (PowerShell-Pipes zerstören Binärdaten)
        Invoke-Native docker @("exec", $container, "pg_dump", "-U", $local["POSTGRES_USER"], "-d", $local["POSTGRES_DB"],
            "-Fc", "--no-owner", "--no-acl", "-f", "/tmp/space_game_deploy.dump")
        Invoke-Native docker @("cp", "${container}:/tmp/space_game_deploy.dump", (Join-Path $Stage "db.dump"))
        & docker exec $container rm -f /tmp/space_game_deploy.dump | Out-Null
        $sizeMb = [math]::Round((Get-Item (Join-Path $Stage "db.dump")).Length / 1MB, 1)
        Write-Host "   Datenbank-Dump: $sizeMb MB"

        # MFA-Secrets sind mit dem lokalen SECRET_KEY verschlüsselt -> auf Prod umschlüsseln
        $localKey = (& docker exec space_game_local_django python manage.py shell -c "from django.conf import settings; print(settings.SECRET_KEY)" 2>$null | Select-Object -Last 1)
        if ($LASTEXITCODE -ne 0 -or -not $localKey) { throw "Konnte den lokalen SECRET_KEY nicht lesen (läuft space_game_local_django?)" }
        [IO.File]::WriteAllText((Join-Path $Stage "mfa_old_key"), $localKey.Trim(), $Utf8NoBom)

        $media = Join-Path $Root "space_game\media"
        if (Test-Path $media) {
            Write-Step "Packe Media-Dateien (Uploads)"
            Invoke-Native $Tar @("-czf", (Join-Path $Stage "media.tar.gz"), "-C", $media, ".")
        }
    }

    # --- 3. Code-Bundle ------------------------------------------------------
    Write-Step "Packe Code"
    Push-Location $Root
    try {
        $files = & git ls-files -co --exclude-standard
        if ($LASTEXITCODE -ne 0) { throw "git ls-files fehlgeschlagen" }
        $files = @($files | Where-Object { $_ -notlike ".envs/*" -and (Test-Path -LiteralPath $_ -PathType Leaf) })
        $files += @(".envs/.production/.django", ".envs/.production/.postgres")
        $listFile = Join-Path $Stage "files.txt"
        [IO.File]::WriteAllText($listFile, (($files -join "`n") + "`n"), $Utf8NoBom)
        Invoke-Native $Tar @("-czf", (Join-Path $Stage "bundle.tar.gz"), "-T", $listFile)
        Remove-Item $listFile
    } finally { Pop-Location }
    Copy-Item (Join-Path $PSScriptRoot "remote-deploy.sh") (Join-Path $Stage "remote-deploy.sh")

    # --- 4. Hochladen & auf dem Server deployen ----------------------------------
    $remoteStage = "/tmp/space_game_deploy_" + (Split-Path $Stage -Leaf).Split("_")[-1]
    Write-Step "Lade Dateien nach ${Server}:$remoteStage hoch"
    Invoke-Native ssh ($SshArgs + @($Server, "mkdir -p $remoteStage && chmod 700 $remoteStage"))
    $upload = @(Get-ChildItem $Stage -File | ForEach-Object { $_.FullName })
    Invoke-Native scp ($ScpArgs + $upload + @("${Server}:$remoteStage/"))

    Write-Step "Deploy auf dem Server"
    $remoteCmd = "sed -i 's/\r`$//' $remoteStage/remote-deploy.sh && " +
                 "APP_DIR='$RemoteDir' APP_PORT='$Port' SITE_DOMAIN='${HostName}:$Port' STAGE_DIR='$remoteStage' " +
                 "bash $remoteStage/remote-deploy.sh"
    # -t: damit sudo ggf. nach dem Passwort fragen kann
    Invoke-Native ssh ($SshArgs + @("-t", $Server, $remoteCmd))
}
finally {
    if (Test-Path $Stage) { Remove-Item -Recurse -Force $Stage }
}

Write-Host ""
Write-Host "======================================================" -ForegroundColor Green
Write-Host " Space Game läuft:   $PublicUrl" -ForegroundColor Green
Write-Host " Admin:              $PublicUrl/$adminUrl" -ForegroundColor Green
Write-Host " Secrets:            $EnvDir" -ForegroundColor Green
Write-Host "======================================================" -ForegroundColor Green
if ($NoData) {
    Write-Host "Ohne Daten-Sync deployt. Admin-User anlegen (falls noch keiner existiert):"
    Write-Host "  ssh $Server `"cd $RemoteDir && sudo docker compose -p space_game -f docker-compose.production.yml -f docker-compose.ip.yml run --rm django python manage.py createsuperuser`""
}
