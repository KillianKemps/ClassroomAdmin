from flask import render_template

from .. import app
from ..utils import allowed_file, process_status


@app.route('/poll')
def poll():

    if process_status.creating_classrooms:
        return render_template('success.html'), 202
    else:
        if process_status.error:
            # Reset error before returning it
            process_status.error = False
            message = process_status.error_message
            process_status.error_message = ''
            return render_template('failure.html', error=message), 500
        else:
            return render_template('success.html'), 200

