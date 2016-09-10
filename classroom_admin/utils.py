from . import app


# For a given file, return whether it's an allowed type or not
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

class process_status():
    creating_classrooms = False
    error = False
    error_message = ''

def manage_error(error):
    app.logger.exception('Caught exception {0}'.format(error))
    process_status.creating_classrooms = False
    process_status.error = True
    process_status.error_message = error
    raise
