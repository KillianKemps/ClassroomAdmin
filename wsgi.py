import uuid

from flask_socketio import SocketIO

from classroom_admin import application

application.secret_key = str(uuid.uuid4())
application.debug = False

if __name__ == "__main__":
    import uuid
    application.secret_key = str(uuid.uuid4())
    application.debug = False
    socketio = SocketIO(application)
    socketio.run(application)
