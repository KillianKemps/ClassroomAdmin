from flask import render_template

from .. import app
from ..utils import allowed_file, process_status


@app.route('/poll-emails')
def poll_emails():

    if process_status.sending_emails:
        return render_template('success.html'), 202
    else:
        if process_status.email_error:
            # Reset error before returning it
            process_status.email_error = False
            message = process_status.email_error_message
            process_status.email_error_message = ''
            return render_template('failure.html', error=message), 500
        else:
            return render_template('success.html'), 200
