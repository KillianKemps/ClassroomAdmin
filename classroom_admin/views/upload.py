import os

import flask

from .. import app
from ..utils import allowed_file


@app.route('/upload', methods=['POST'])
def upload():
    # Get the name of the uploaded file
    file = flask.request.files['file']
    # Check if the file is one of the allowed types/extensions
    if file and allowed_file(file.filename):
        # Make the filename safe, remove unsupported chars
        # filename = secure_filename(file.filename)

        # Create folder if is doesn't exist
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])

        # Move the file form the temporal folder to
        # the upload folder we setup
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'courses_list.csv'))

        print('New file uploaded')
        # Redirect the user to the uploaded_file route, which
        # will basicaly show on the browser the uploaded file
        return flask.redirect(flask.url_for('index'))


