from flask import Flask
from flask_assets import Environment
from flask_socketio import SocketIO

import yaml


app = Flask(__name__)
assets = Environment(app)

app.config['SECRET_KEY'] = 'secret!'

# This is the path to the upload directory
app.config['UPLOAD_FOLDER'] = 'uploads/'
# This is the path to the configuration directory
app.config['CONF_FOLDER'] = 'classroom_admin/conf/'
# These are the extension that we are accepting to be uploaded
app.config['ALLOWED_EXTENSIONS'] = set(['csv'])

f = open('classroom_admin/conf/' + 'course.yaml')
app.config['COURSE_CONF'] = yaml.safe_load(f)
f.close()

f = open('classroom_admin/conf/' + 'email.yaml')
app.config['EMAIL_CONF'] = yaml.safe_load(f)
f.close()

assets.debug = True
app.config['ASSETS_DEBUG'] = True

if not app.debug:
    import logging
    from logging import FileHandler, Formatter
    from logging.handlers import RotatingFileHandler

    error_file_handler = FileHandler('error.log')
    error_file_handler.setFormatter(Formatter(
        '%(asctime)s %(levelname)s: %(message)s '
        '[in %(pathname)s:%(lineno)d]'
    ))
    error_file_handler.setLevel(logging.WARNING)
    app.logger.addHandler(error_file_handler)

    rotating_handler = RotatingFileHandler('stdout.log', maxBytes=10000, backupCount=1)
    rotating_handler.setFormatter(Formatter(
        '%(asctime)s %(levelname)s: %(message)s '
        '[in %(pathname)s:%(lineno)d]'
    ))
    rotating_handler.setLevel(logging.INFO)
    app.logger.addHandler(rotating_handler)

    app.logger.setLevel(logging.INFO)

socketio = SocketIO(app)
application = app

from .views import index, poll, poll_emails, create, upload, auth, send_email
