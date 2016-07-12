import csv
import os
import threading
import httplib2

import flask
from flask import render_template
from apiclient import discovery, errors
from oauth2client import client

from .. import app
from ..utils import process_status


@app.route('/create', methods=['POST'])
def create():
    print(flask.request.form['courses'])
    print('0'*80)
    print('0'*80)
    print('0'*80)

    emails = {}

    def get_emails(http_auth, mailing_list):
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

    # Convert parameter into list of integer
    selected_courses = flask.request.form['courses']
    selected_courses = [int(i) for i in selected_courses.split(',')]

    def create_classrooms(selected_courses):
        # Set status of the app as being busy
        process_status.creating_classrooms = True
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
                        members = get_emails(http_auth, course['Liste de diffusion'])

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
                # Set status of the app as free again
                process_status.creating_classrooms = False
                print('+'*80)
                print('+'*80)
                print('+'*80)

    if 'credentials' not in flask.session:
        return flask.redirect(flask.url_for('oauth2callback'))

    credentials = client.OAuth2Credentials.from_json(flask.session['credentials'])

    if credentials.access_token_expired:
        return flask.redirect(flask.url_for('oauth2callback'))
    else:
        threading.Thread(target=create_classrooms, args=(selected_courses,)).start()
        return render_template('success.html'), 202