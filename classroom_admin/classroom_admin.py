import csv
import os

import simplejson
import httplib2
import flask

from apiclient import discovery, errors
from oauth2client import client

from flask import render_template
from flask import Flask
from werkzeug import secure_filename
from flask_assets import Environment, Bundle


app = Flask(__name__)
assets = Environment(app)

# This is the path to the upload directory
app.config['UPLOAD_FOLDER'] = 'uploads/'
# These are the extension that we are accepting to be uploaded
app.config['ALLOWED_EXTENSIONS'] = set(['csv'])

# For a given file, return whether it's an allowed type or not
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


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

        if os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], 'courses_list.csv')) :
            with open(os.path.join(app.config['UPLOAD_FOLDER'], 'courses_list.csv')) as csvfile:
                reader = csv.DictReader(csvfile)
                return render_template('courses.html', courses=reader)
        else:
            return render_template('index.html')


@app.route('/create', methods=['POST'])
def create():
    print(flask.request.form['courses'])
    print('0'*80)
    print('0'*80)
    print('0'*80)

    emails = {}

    def get_emails(mailing_list):
        print('$'*80)
        if mailing_list in emails:
            print('Mailing list already exist')
            return emails[mailing_list]
        else:
            print('Getting mailing list')
            discov_service = discovery.build('admin', 'directory_v1', http=http_auth)
            students = discov_service.members().list(groupKey=mailing_list).execute()
            emails[mailing_list] = students.get('members', [])
            return emails[mailing_list]

    if 'credentials' not in flask.session:
        return flask.redirect(flask.url_for('oauth2callback'))

    credentials = client.OAuth2Credentials.from_json(flask.session['credentials'])

    if credentials.access_token_expired:
        return flask.redirect(flask.url_for('oauth2callback'))
    else:
        http_auth = credentials.authorize(httplib2.Http())
        classroom_service = discovery.build('classroom', 'v1', http=http_auth)
        if os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], 'courses_list.csv')) :
            with open(os.path.join(app.config['UPLOAD_FOLDER'], 'courses_list.csv')) as csvfile:
                reader = csv.DictReader(csvfile)

                # Create batch for classroom requests
                def callback(request_id, response, exception):
                    if exception is not None:
                        error = simplejson.loads(exception.content).get('error')
                        if(error.get('code') == 409):
                            print('User "{0}" is already a member of this course.'.format(
                                response['userId']))
                        else:
                            print('Error adding user "{0}" to the course: {1}'.format(
                                response['userId'], exception))
                    else:
                        print('User "{0}" added as a {1} to the course.'.format(
                            response['userId'], response['role']))

                members_batch = classroom_service.new_batch_http_request(callback=callback)

                print('M'*80)
                print('M'*80)
                print('M'*80)
                # Convert parameter into list of integer
                selected_courses = flask.request.form['courses']
                selected_courses = [int(i) for i in selected_courses.split(',')]

                for index, course in enumerate(reader):
                    print('%'*80)
                    if index in selected_courses:
                        print('index: ', index)
                        print('%'*80)

                        # Create course
                        body = {
                            'ownerId': course['Moderateur'],
                            'name': course['Cours'],
                            'section': course['Année scolaire'] + ' - ' + course['Domaine'] + ' - ' + course['Promotion'],
                            'courseState': 'ACTIVE'
                        }

                        result = classroom_service.courses().create(body=body).execute()

                        print('*'*80)
                        print(result)

                        # Add teacher to course
                        teacher = {
                            'courseId': result['id'],
                            'userId': course['Mail wsf de l\'intervenant'],
                            'role': 'TEACHER'
                        }

                        request = classroom_service.invitations().create(body=teacher)
                        members_batch.add(request, request_id=teacher['userId'] + str(index))

                        print (u'User {0} was added to the batch as a teacher for course with ID "{1}"'
                            .format(teacher['userId'],
                            teacher['courseId']))

                        # Add students to course
                        members = get_emails(course['Liste de diffusion'])

                        for member in members:
                            if member['email'].endswith('@etu-webschoolfactory.fr'):
                                student = {
                                    'courseId': result['id'],
                                    'userId': member['email'],
                                    'role': 'STUDENT'
                                }

                                try:
                                    request = classroom_service.invitations().create(body=student)
                                    members_batch.add(request, request_id=member['email'] + str(index))

                                    print (u'User {0} was added to the batch as a student for course with ID "{1}"'
                                        .format(student['userId'],
                                        student['courseId']))
                                except KeyError as e:
                                    print('The user has already been added: ', e)

                print('!'*80)
                print('!'*80)
                print('!'*80)
                members_batch.execute(http=http_auth)
                print('+'*80)
                print('+'*80)
                print('+'*80)

        return render_template('success.html')

@app.route('/read')
def read():
    with open('test_courses.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        return render_template('courses.html', courses=reader)

@app.route('/upload', methods=['POST'])
def upload():
    # Get the name of the uploaded file
    file = flask.request.files['file']
    # Check if the file is one of the allowed types/extensions
    if file and allowed_file(file.filename):
        # Make the filename safe, remove unsupported chars
        # filename = secure_filename(file.filename)
        # Move the file form the temporal folder to
        # the upload folder we setup
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])

        file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'courses_list.csv'))
        # Redirect the user to the uploaded_file route, which
        # will basicaly show on the browser the uploaded file
        return flask.redirect(flask.url_for('index'))

@app.route('/mailing-list')
def get_mailing_list():
    print('*'*80)
    if 'credentials' not in flask.session:
        return flask.redirect(flask.url_for('oauth2callback'))

    credentials = client.OAuth2Credentials.from_json(flask.session['credentials'])

    if credentials.access_token_expired:
        return flask.redirect(flask.url_for('oauth2callback'))
    else:
        http_auth = credentials.authorize(httplib2.Http())
        service = discovery.build('admin', 'directory_v1', http=http_auth)
        if os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], 'courses_list.csv')) :
            with open(os.path.join(app.config['UPLOAD_FOLDER'], 'courses_list.csv')) as csvfile:
                reader = csv.DictReader(csvfile)
                course = next(reader)
                results = service.members().list(groupKey=course['Liste de diffusion']).execute()
                print('result: ', results)
                users = results.get('members', [])

                for user in users:
                    if user['email'].endswith('etu-webschoolfactory.fr'):
                        print('{0} '.format(user['email']))

        return render_template('success.html')


@app.route('/oauth2callback')
def oauth2callback():
    scopes = ['https://www.googleapis.com/auth/classroom.courses', 'https://www.googleapis.com/auth/classroom.rosters', 'https://www.googleapis.com/auth/admin.directory.group.readonly']
    flow = client.flow_from_clientsecrets(
        'client_secret.json',
        scopes,
        redirect_uri=flask.url_for('oauth2callback', _external=True))
    if 'code' not in flask.request.args:
        auth_uri = flow.step1_get_authorize_url()
        return flask.redirect(auth_uri)
    else:
        auth_code = flask.request.args.get('code')
        credentials = flow.step2_exchange(auth_code)
        flask.session['credentials'] = credentials.to_json()
        return flask.redirect(flask.url_for('index'))


assets.debug = True
app.config['ASSETS_DEBUG'] = True

application = app
