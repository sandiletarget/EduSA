web: bash -lc "python manage.py collectstatic --noinput; python manage.py migrate --noinput; gunicorn edusa.wsgi --bind 0.0.0.0:$PORT"
