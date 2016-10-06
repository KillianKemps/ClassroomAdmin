import os
import csv

import flask
from flask import render_template
from flask_socketio import SocketIO, emit
from oauth2client import client

from .. import app

socketio = SocketIO(app)


@app.route('/')
def index():
    if 'credentials' not in flask.session:
        return flask.redirect(flask.url_for('oauth2callback'))

    credentials = client.OAuth2Credentials.from_json(
        flask.session['credentials'])

    if credentials.access_token_expired:
        return flask.redirect(flask.url_for('oauth2callback'))
    else:
        filename = os.path.join(app.config['UPLOAD_FOLDER'], 'courses_list.csv')
        if os.path.isfile(filename) :
            with open(filename) as csvfile:
                reader = csv.DictReader(csvfile)
                return render_template('courses.html', courses=reader)
        else:
            return render_template('index.html')


@socketio.on('my event')
def test_message(message):
    print('Socket: received message: ' + message['data'])
    emit('my response', {'data': message['data']})

@socketio.on('my broadcast event')
def test_message(message):
    print('Socket: received message: ' + message['data'])
    emit('my response', {'data': message['data']}, broadcast=True)

@socketio.on('connect')
def test_connect():
    print('Socket: got connected')
    emit('my response', {'data': 'Connected'})

@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')
