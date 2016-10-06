#!/bin/bash

# WORKDIR
cd /var/app

# Start HTTP server.
uwsgi --http :8080 --chdir /var/app --gevent 1000 --http-websockets --master --processes $UWSGI_NUM_PROCESSES --wsgi-file wsgi.py --callable application
