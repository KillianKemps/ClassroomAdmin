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

application = app

from .views import index, poll, create, upload, auth
