#!/bin/bash

# WORKDIR
cd /var/app

# Start HTTP server.
uwsgi --http :8080 --chdir /var/app --wsgi-file wsgi.py --master --processes $UWSGI_NUM_PROCESSES --threads $UWSGI_NUM_THREADS --touch-reload $SERVICE_NAME/settings.py --uid $UWSGI_UID --gid $UWSGI_GID --lazy-apps --memory-report
