#!/bin/bash

# WORKDIR
cd /var/app

# Start HTTP server.
gunicorn -b 0.0.0.0:8000 -k gevent -w 1 classroom_admin:app
