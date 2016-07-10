FROM       python:3.5.1

# based on https://github.com/aws/aws-eb-python-dockerfiles
MAINTAINER Killian Kemps <killian.kemps@etu-webschoolfactory.fr>

WORKDIR    /var/app

RUN        /usr/local/bin/pip install uwsgi
RUN        useradd uwsgi -s /bin/false

COPY       classroom_admin /var/app/
COPY       wsgi.py /var/app/
COPY       requirements.txt /var/app/
RUN        if [ -f /var/app/requirements.txt ]; then /usr/local/bin/pip install -r /var/app/requirements.txt; fi

ENV        UWSGI_NUM_PROCESSES    1
ENV        UWSGI_NUM_THREADS      50
ENV        UWSGI_UID              uwsgi
ENV        UWSGI_GID              uwsgi
ENV        UWSGI_LOG_FILE         /var/log/uwsgi/uwsgi.log

ENV        SERVICE_NAME           classroom_admin

EXPOSE     8080

ADD        docker/service-start.sh /
CMD        ["/service-start.sh"]
