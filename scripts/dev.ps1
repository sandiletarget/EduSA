# EduSA Windows Dev Runner
# Starts Django dev server + Celery worker (solo) using safe SQLite settings.
# Idempotent: re-running starts new consoles without breaking existing ones.

$ErrorActionPreference = "Stop"

# Resolve project root (this script lives in scripts/)
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

# Prefer local venv if present
$Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $Python)) {
    $Python = "python"
}

Write-Host "Starting EduSA development environment..." -ForegroundColor Cyan

# Common env for dev (safe for SQLite + in-memory Celery broker)
$envSetup = @(
    '$env:DJANGO_DEBUG="1"',
    '$env:CELERY_BROKER_URL="memory://"',
    '$env:CELERY_RESULT_BACKEND="cache+memory://"',
    '$env:PYTHONUNBUFFERED="1"'
) -join '; '

# Start Django dev server in a new console
$djangoCmd = "$envSetup; & `"$Python`" manage.py runserver"
Start-Process -FilePath "powershell" -ArgumentList "-NoExit", "-Command", $djangoCmd | Out-Null
Write-Host "Django server running" -ForegroundColor Green

# Start Celery worker in a new console (solo mode for Windows)
$celeryCmd = "$envSetup; celery -A edusa worker -l info --pool=solo"
Start-Process -FilePath "powershell" -ArgumentList "-NoExit", "-Command", $celeryCmd | Out-Null
Write-Host "Celery worker running" -ForegroundColor Green

# Optional: quick AI task test (uncomment to enqueue)
# $testCmd = "$envSetup; & `"$Python`" manage.py shell -c \"from backend.ai.tasks import generate_summary; generate_summary.delay(1); print('Queued summary task')\""
# Start-Process -FilePath "powershell" -ArgumentList "-NoExit", "-Command", $testCmd | Out-Null

Write-Host "Dev environment ready." -ForegroundColor Cyan
Write-Host "Tip: stop servers by closing the opened PowerShell windows." -ForegroundColor Yellow
