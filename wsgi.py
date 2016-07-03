import uuid

from classroom_admin.classroom_admin import application

application.secret_key = str(uuid.uuid4())
application.debug = False

if __name__ == "__main__":
    import uuid
    application.secret_key = str(uuid.uuid4())
    application.debug = False
    application.run()
