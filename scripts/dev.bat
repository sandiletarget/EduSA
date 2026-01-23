@echo off
REM EduSA Windows Dev Runner
REM Starts Django dev server + Celery worker (solo) using safe SQLite settings.
REM Idempotent: re-running starts new consoles without breaking existing ones.

setlocal

REM Set project root (this script lives in scripts\)
set PROJECT_ROOT=%~dp0..
cd /d %PROJECT_ROOT%

REM Prefer local venv if present
set PYTHON=%PROJECT_ROOT%\.venv\Scripts\python.exe
if not exist "%PYTHON%" set PYTHON=python

echo Starting EduSA development environment...

REM Common env for dev (safe for SQLite + in-memory Celery broker)
set DJANGO_DEBUG=1
set CELERY_BROKER_URL=memory://
set CELERY_RESULT_BACKEND=cache+memory://
set PYTHONUNBUFFERED=1

REM Start Django dev server in a new console
start "EduSA Django" cmd /k "%PYTHON% manage.py runserver"
echo Django server running

REM Start Celery worker in a new console (solo mode for Windows)
start "EduSA Celery" cmd /k "celery -A edusa worker -l info --pool=solo"
echo Celery worker running

REM Optional: quick AI task test (uncomment to enqueue)
REM start "EduSA AI Test" cmd /k "%PYTHON% manage.py shell -c ""from backend.ai.tasks import generate_summary; generate_summary.delay(1); print('Queued summary task')"""

echo Dev environment ready.
echo Tip: stop servers by closing the opened windows.
endlocal
