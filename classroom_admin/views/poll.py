from flask import render_template

from .. import app
from ..utils import allowed_file, process_status


@app.route('/poll')
def poll():

    print('Is creating classrooms: ', process_status.creating_classrooms)
    if process_status.creating_classrooms:
        return render_template('success.html'), 202
    else:
        return render_template('success.html'), 200

