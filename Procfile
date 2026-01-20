web: bash -lc "python manage.py collectstatic --noinput; python manage.py migrate --noinput; daphne -b 0.0.0.0 -p $PORT edusa.asgi:application"
