from . import app


# For a given file, return whether it's an allowed type or not
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

class process_status():
    creating_classrooms = False
    sending_emails = False
    error = False
    email_error = False
    error_message = ''
    email_error_message = ''

def manage_error(error, index=None):
    if index is not None:
        app.logger.exception('Caught exception for classroom number {0}: {1}\
            '.format(index, error))
        process_status.error_message = 'On course n°' + str(index) + ' :' + str(error)
    else:
        app.logger.exception('Caught exception {0}'.format(error))
        process_status.error_message = error

    process_status.creating_classrooms = False
    process_status.error = True
    raise

def manage_email_error(error, index=None):
    if index is not None:
        app.logger.exception('Caught exception for classroom number {0}: {1}\
            '.format(index, error))
        process_status.email_error_message = 'On course n°' + str(index) + ' :' + str(error)
    else:
        app.logger.exception('Caught exception {0}'.format(error))
        process_status.email_error_message = error

    process_status.sending_emails = False
    process_status.email_error = True
    raise
