uwsgi -d --module=eam_backend.wsgi:application \
    --env DJANGO_SETTINGS_MODULE=eam_backend.settings \
    --master \
    --http=0.0.0.0:8000 \
    --processes=5 \
    --harakiri=20 \
    --max-requests=5000 \
    --vacuum &&
echo 'hello' &&
daphne -b 0.0.0.0 -p 8000 --application-close-timeout 300 eam_backend.asgi:application
# uwsgi --module=eam_backend.wsgi:application \
#     --env DJANGO_SETTINGS_MODULE=eam_backend.settings \
#     --master \
#     --http=0.0.0.0:8000 \
#     --processes=5 \
#     --harakiri=20 \
#     --max-requests=5000 \
#     --vacuum \
#     --enable-threads
