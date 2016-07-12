import csv
import os
import threading
import httplib2
import base64
from email.mime.text import MIMEText
import simplejson

import flask
from flask import render_template
from apiclient import discovery, errors
from oauth2client import client

from .. import app
from ..utils import process_status
from ..templates.email import TEMPLATE


EMAILS = {}


# Get individual emails from mailing list
def get_emails(http_auth, mailing_list):
    print('$'*80)
    if mailing_list in EMAILS:
        print('Mailing list already exist')
        return EMAILS[mailing_list]
    else:
        print('Getting mailing list')
        service = discovery.build('admin', 'directory_v1', http=http_auth)
        students = service.members().list(groupKey=mailing_list).execute()
        EMAILS[mailing_list] = students.get('members', [])
        return EMAILS[mailing_list]

def send_email(http_auth, email_info):
    service = discovery.build('gmail', 'v1', http=http_auth)

    text = TEMPLATE.format(
        email_info['civilite'],
        email_info['prenom'],
        email_info['nom'],
        email_info['lien'],
        email_info['adresse_email'],
        email_info['cours'],
        email_info['promotion'],
        email_info['liste_diffusion'],
        email_info['code'])

    message = MIMEText(text, 'html')
    message['To'] = email_info['adresse_email']
    message['From'] = 'me'
    message['Subject'] = 'Création du classroom {0}'.format(email_info['cours'])
    raw = base64.urlsafe_b64encode(message.as_bytes())
    raw = raw.decode()
    body = {'raw': raw}

    try:
        message = (service.users().messages().send(userId='me', body=body)
        .execute())
        print('Message Id: %s' % message['id'])
        return message
    except errors.HttpError as error:
        print('An error occurred: %s' % error)

    return message

# Callback function for each user been added to a classroom
def callback(request_id, response, exception):
    if exception is not None:
        error = simplejson.loads(exception.content).get('error')
        if(error.get('code') == 409):
            print('User "{0}" is already a member of this course.'.format(
                response['userId']))
        else:
            print('Error adding user "{0}" to the course: {1}'.format(
                request_id,
                error))
    else:
        print('User "{0}" added as a {1} to the course.'.format(
            response['userId'], response['role']))


def create_classrooms(selected_courses, credentials):
    # Set status of the app as being busy
    process_status.creating_classrooms = True
    http_auth = credentials.authorize(httplib2.Http())
    classroom_service = discovery.build('classroom', 'v1', http=http_auth)
    filename = os.path.join(app.config['UPLOAD_FOLDER'], 'courses_list.csv')

    if os.path.isfile(filename) :
        with open(filename) as csvfile:
            reader = csv.DictReader(csvfile)

            # Create batch for classroom requests
            members_batch = classroom_service.new_batch_http_request(
                callback=callback)

            for index, course in enumerate(reader):
                if index in selected_courses:
                    print('%'*80)
                    print('Creating classroom ', index)

                    # Create course
                    body = {
                        'ownerId': course['Moderateur'],
                        'name': course['Cours'],
                        'section': '{0} - {1} - {2}'.format(
                            course['Année scolaire'],
                            course['Domaine'],
                            course['Promotion']),
                        'courseState': 'ACTIVE'
                    }

                    result = classroom_service.courses() \
                        .create(body=body).execute()

                    print('*'*80)
                    print(result)

                    # Add teacher to course
                    teacher = {
                        'userId': course['Mail wsf de l\'intervenant'],
                    }

                    try:
                        teacher = classroom_service.courses() \
                            .teachers().create(
                                courseId=result['id'],
                                body=teacher).execute()
                        print (u'User {0} was added as a teacher to '
                                'the course with ID "{1}"'
                                .format(teacher.get('profile')
                                    .get('name').get('fullName'),
                                    result['id']))
                    except errors.HttpError as e:
                        error = simplejson.loads(e.content).get('error')
                        if(error.get('code') == 409):
                            print(u'User "{0}" is already a member '
                                'of this course.'.format(
                                teacher['userId']))
                        else:
                            raise

                    email_info = {
                        'civilite': course['Civilité'],
                        'prenom': course['Prenom de l\'intervenant'],
                        'nom': course['Nom de l\'intervenant'],
                        'lien': result['alternateLink'],
                        'adresse_email': course['Mail wsf de l\'intervenant'],
                        'promotion': course['Promotion'],
                        'cours': course['Cours'],
                        'liste_diffusion': course['Liste de diffusion'],
                        'code': result['enrollmentCode']
                    }

                    send_email(http_auth, email_info)

                    # Add students to course
                    members = get_emails(
                        http_auth, course['Liste de diffusion'])

                    for member in members:
                        if member['email'].endswith('@etu-webschoolfactory.fr'):
                            student = {
                                'courseId': result['id'],
                                'userId': member['email'],
                                'role': 'STUDENT'
                            }

                            try:
                                request = classroom_service \
                                    .invitations().create(body=student)
                                members_batch.add(
                                    request,
                                    request_id=member['email'] + str(index))

                                print (u'User {0} was added to the batch as '
                                       'a student for course with ID "{1}"'
                                    .format(student['userId'],
                                    student['courseId']))
                            except KeyError as e:
                                print('The user has already been added: ', e)

            members_batch.execute(http=http_auth)
            # Set status of the app as free again
            process_status.creating_classrooms = False
            print('*'*80)
            print('Finished creating all classrooms')


@app.route('/create', methods=['POST'])
def create():
    print('*'*80)
    print('Preparing to create classrooms')

    # Convert parameter into list of integer
    selected_courses = flask.request.form['courses']
    selected_courses = [int(i) for i in selected_courses.split(',')]

    if 'credentials' not in flask.session:
        return flask.redirect(flask.url_for('oauth2callback'))

    credentials = client.OAuth2Credentials.from_json(
        flask.session['credentials'])

    if credentials.access_token_expired:
        return flask.redirect(flask.url_for('oauth2callback'))
    else:
        threading.Thread(
            target=create_classrooms,
            args=(selected_courses, credentials)).start()
        return render_template('success.html'), 202
