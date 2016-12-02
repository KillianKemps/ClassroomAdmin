import uuid

from classroom_admin import application
from classroom_admin import socketio

application.secret_key = str(uuid.uuid4())
application.debug = False

if __name__ == "__main__":
    import uuid
    application.secret_key = str(uuid.uuid4())
    application.debug = False
    socketio.run(application)
