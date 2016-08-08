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


EMAILS = {}


# Get individual emails from mailing list
def get_emails(http_auth, mailing_list):
    print('$'*80)
    if mailing_list in EMAILS:
        print('Mailing list already exist')
        app.logger.info('Mailing list already exist')
        return EMAILS[mailing_list]
    else:
        print('Getting mailing list')
        app.logger.info('Getting mailing list')
        service = discovery.build('admin', 'directory_v1', http=http_auth)
        students = service.members().list(groupKey=mailing_list).execute()
        EMAILS[mailing_list] = students.get('members', [])
        return EMAILS[mailing_list]

def create_email(email_info, http_auth):
    service = discovery.build('gmail', 'v1', http=http_auth)
    EMAIL_CONF = app.config['EMAIL_CONF']

    text = EMAIL_CONF['content-format'].format(
        *[email_info[val] for val in EMAIL_CONF['content-value']])

    message = MIMEText(text, 'html')
    message['To'] = email_info[EMAIL_CONF['to']]
    message['From'] = 'me'
    message['Subject'] = EMAIL_CONF['subject-format'].format(
        email_info[EMAIL_CONF['subject-value']])
    raw = base64.urlsafe_b64encode(message.as_bytes())
    raw = raw.decode()
    body = {'raw': raw}

    message = service.users().messages().send(userId='me', body=body)
    return message

# Callback function for each user been added to a classroom
def member_callback(request_id, response, exception):
    if exception is not None:
        error = simplejson.loads(exception.content).get('error')
        if(error.get('code') == 409):
            print('User "{0}" is already a member of this course.'.format(
                request_id))
            app.logger.error('User "{0}" is already a member of '
                'this course.'.format(request_id))
        else:
            print('Error adding user "{0}" to the course: {1}'.format(
                request_id,
                error))
            app.logger.error('Error adding user "{0}" to the course: {1}' \
                .format(
                    request_id,
                    error))
    else:
        print('User "{0}" added as a student to the course.'.format(
            response['userId']))
        app.logger.info('User "{0}" added as a student to the course.'.format(
            response['userId']))

# Callback function for each teacher been added to a classroom
def teacher_callback(request_id, response, exception):
    if exception is not None:
        error = simplejson.loads(exception.content).get('error')
        if(error.get('code') == 409):
            print('Teacher "{0}" is already a member of this course.'.format(
                request_id))
            app.logger.error('Teacher "{0}" is already a member of '
                'this course.'.format(request_id))
        else:
            print('Error adding teacher "{0}" to the course: {1}'.format(
                request_id,
                error))
            app.logger.error('Error adding teacher "{0}" to the course: {1}' \
                .format(
                    request_id,
                    error))
    else:
        print('User "{0}" added as a teacher to the course.'.format(
            response['userId']))
        app.logger.info('User "{0}" added as a teacher to the course.'.format(
            response['userId']))

# Callback function for emails sent to teachers
def email_callback(request_id, response, exception):
    if exception is not None:
        error = simplejson.loads(exception.content).get('error')
        print('An error occurred while sending email: %s' % error)
        app.logger.error('An error occurred while sending email: %s' % error)


def create_classrooms(selected_courses, credentials):
    # Set status of the app as being busy
    process_status.creating_classrooms = True
    http_auth = credentials.authorize(httplib2.Http())
    classroom_service = discovery.build('classroom', 'v1', http=http_auth)
    email_service = discovery.build('gmail', 'v1', http=http_auth)
    filename = os.path.join(app.config['UPLOAD_FOLDER'], 'courses_list.csv')

    if os.path.isfile(filename) :
        with open(filename) as csvfile:
            reader = csv.DictReader(csvfile)

            # Create batch for classroom students requests
            members_batch = classroom_service.new_batch_http_request(
                callback=member_callback)

            # Create batch for classroom teachers requests
            teachers_batch = classroom_service.new_batch_http_request(
                callback=teacher_callback)

            # Create batch for email requests
            emails_batch = email_service.new_batch_http_request(
                callback=email_callback)

            for index, course in enumerate(reader):
                if index in selected_courses:
                    print('Creating classroom ', index)
                    app.logger.info('Creating classroom %s', index)

                    print('!'*80)
                    COURSE_CONF = app.config['COURSE_CONF']
                    print(COURSE_CONF)

                    # Create course
                    body = {
                        'ownerId': course[COURSE_CONF['ownerId']],
                        'name': course[COURSE_CONF['name']],
                        'section': COURSE_CONF['section-format'].format(
                            *[course[val] for val in COURSE_CONF[
                                'section-values']]),
                        'courseState': 'ACTIVE'
                    }

                    print(':'*80)
                    print(body)

                    created_course = classroom_service.courses() \
                        .create(body=body).execute()

                    print(created_course)
                    app.logger.info(created_course)

                    # Add teacher to course
                    teacher = {
                        'userId': course[COURSE_CONF['teacher']],
                    }

                    teacher = classroom_service.courses() \
                        .teachers().create(
                            courseId=created_course['id'],
                            body=teacher)

                    teachers_batch.add(teacher, request_id=str(index))

                    # Merge created course and initial course infos
                    email_info = {}
                    email_info.update(course)
                    email_info.update(created_course)

                    emails_batch.add(create_email(email_info, http_auth),
                        request_id=str(index))

                    # Add students to course
                    members = get_emails(
                        http_auth, course['Liste de diffusion'])

                    for member in members:
                        if member['email'].endswith(
                                COURSE_CONF['member-email-domain']):
                            student = {
                                'courseId': created_course['id'],
                                'userId': member['email'],
                            }

                            try:
                                request = classroom_service.courses() \
                                    .students().create(body=student,
                                        enrollmentCode=created_course[
                                            'enrollmentCode'],
                                        courseId=student['courseId'])
                                members_batch.add(
                                    request,
                                    request_id=member['email'] + str(index))

                                print (u'User {0} was added to the batch as '
                                       'a student for course with ID "{1}"'
                                    .format(student['userId'],
                                    student['courseId']))
                                app.logger.info(u'User {0} was added to the '
                                    'batch as a student for course '
                                    'with ID "{1}"'
                                    .format(student['userId'],
                                    student['courseId']))
                            except KeyError as e:
                                print('The user has already been added: ', e)
                                app.logger.error('The user has already '
                                    'been added: %s', e)

            teachers_batch.execute(http=http_auth)
            members_batch.execute(http=http_auth)
            emails_batch.execute(http=http_auth)
            # Set status of the app as free again
            process_status.creating_classrooms = False
            print('*'*80)
            print('Finished creating all classrooms')
            app.logger.info('Finished creating all classrooms')


@app.route('/create', methods=['POST'])
def create():
    print('*'*80)
    print('Preparing to create classrooms')
    app.logger.info('Preparing to create classrooms')

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
