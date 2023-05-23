#!/bin/sh
python3 manage.py makemigrations Department
python3 manage.py makemigrations User
python3 manage.py makemigrations Asset
python3 manage.py makemigrations Request 
python3 manage.py makemigrations Async
python3 manage.py migrate
# python3 manage.py loaddata db.json

# TODO Start: [Student] Run with uWSGI instead
# python3 manage.py runserver 8000
uwsgi -d --module=eam_backend.wsgi:application \
    --env DJANGO_SETTINGS_MODULE=eam_backend.settings \
    --master \
    --http=0.0.0.0:80 \
    --processes=5 \
    --harakiri=1200 \
    --max-requests=5000 \
    --vacuum &&
daphne -b 0.0.0.0 -p 80 --application-close-timeout 1200 eam_backend.asgi:application
# TODO End: [Student] Run with uWSGI instead
