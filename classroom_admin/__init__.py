from flask import Flask
from flask_assets import Environment


app = Flask(__name__)
assets = Environment(app)

# This is the path to the upload directory
app.config['UPLOAD_FOLDER'] = 'uploads/'
# These are the extension that we are accepting to be uploaded
app.config['ALLOWED_EXTENSIONS'] = set(['csv'])

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

application = app

from .views import index, poll, create, upload, auth
