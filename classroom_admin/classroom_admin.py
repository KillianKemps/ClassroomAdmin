import json
import csv

import httplib2
import flask

from apiclient import discovery
from oauth2client import client

from flask import render_template
from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    if 'credentials' not in flask.session:
        return flask.redirect(flask.url_for('oauth2callback'))

    credentials = client.OAuth2Credentials.from_json(flask.session['credentials'])

    if credentials.access_token_expired:
        return flask.redirect(flask.url_for('oauth2callback'))
    else:
        http_auth = credentials.authorize(httplib2.Http())
        service = discovery.build('classroom', 'v1', http=http_auth)

        results = service.courses().list(pageSize=10).execute()
        courses = results.get('courses', [])
        return render_template('index.html', courses=courses)


@app.route('/create')
def create():
    if 'credentials' not in flask.session:
        return flask.redirect(flask.url_for('oauth2callback'))

    credentials = client.OAuth2Credentials.from_json(flask.session['credentials'])

    if credentials.access_token_expired:
        return flask.redirect(flask.url_for('oauth2callback'))
    else:
        http_auth = credentials.authorize(httplib2.Http())
        service = discovery.build('classroom', 'v1', http=http_auth)
        body = {
            "ownerId": "killian.kemps@etu-webschoolfactory.fr",
            "name": "second_test_course"
        }

        results = service.courses().create(body=body).execute()
        return render_template('success.html')

@app.route('/read')
def read():
    with open('test_courses.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        return render_template('courses.html', courses=reader)


@app.route('/oauth2callback')
def oauth2callback():
    flow = client.flow_from_clientsecrets(
        'client_secret.json',
        scope='https://www.googleapis.com/auth/classroom.courses',
        redirect_uri=flask.url_for('oauth2callback', _external=True))
    if 'code' not in flask.request.args:
        auth_uri = flow.step1_get_authorize_url()
        return flask.redirect(auth_uri)
    else:
        auth_code = flask.request.args.get('code')
        credentials = flow.step2_exchange(auth_code)
        flask.session['credentials'] = credentials.to_json()
        return flask.redirect(flask.url_for('index'))


application = app
