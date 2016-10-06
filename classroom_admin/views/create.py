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
from retrying import retry

from .. import app
from ..utils import process_status, manage_error


EMAILS = {}


# Get individual emails from mailing list
def get_emails(index, http_auth, mailing_list):
    if mailing_list in EMAILS:
        print('Mailing list already exist')
        app.logger.info('Mailing list already exist')
        return EMAILS[mailing_list]
    else:
        print('Getting mailing list')
        app.logger.info('Getting mailing list')
        service = discovery.build('admin', 'directory_v1', http=http_auth)

        try:
            clean_mailing_list = mailing_list.strip()
            students = service.members().list(groupKey=clean_mailing_list).execute()
        except Exception as e:
            manage_error(e, index)

        EMAILS[mailing_list] = students.get('members', [])
        return EMAILS[mailing_list]

# Create email object
def create_email(index, email_info, http_auth):
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

    try:
        message = service.users().messages().send(userId='me', body=body)
    except Exception as e:
        manage_error(e, index)

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
            raise exception
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
            raise exception
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


# Wrap functions to be decorated by @retry. Allows exponential backoff.
@retry(wait_exponential_multiplier=1000,
       wait_exponential_max=10000,
       stop_max_delay=30000)
def exec_alias_creation(alias_request):
    try:
        return alias_request.execute()
    except Exception:
        print('Error while creating alias: Trying again.')
        raise


# Wrap functions to be decorated by @retry. Allows exponential backoff.
@retry(wait_exponential_multiplier=1000,
       wait_exponential_max=10000,
       stop_max_delay=30000)
def exec_classroom_creation(classroom_service, body):
    try:
        return classroom_service.courses().create(body=body).execute()
    except Exception:
        print('Error while creating classroom: Trying again.')
        raise


# Wrap functions to be decorated by @retry. Allows exponential backoff.
@retry(wait_exponential_multiplier=1000,
       wait_exponential_max=10000,
       stop_max_delay=30000)
def exec_teacher_batch(teachers_batch, http_auth):
    try:
        teachers_batch.execute(http=http_auth)
    except Exception:
        print('Error while adding teachers: Trying again.')
        raise


# Wrap functions to be decorated by @retry. Allows exponential backoff.
@retry(wait_exponential_multiplier=1000,
       wait_exponential_max=10000,
       stop_max_delay=30000)
def exec_members_batch(members_batch, http_auth):
    try:
        members_batch.execute(http=http_auth)
    except Exception:
        print('Error while adding members: Trying again.')
        raise


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

            # Enumerate in courses from CSV
            for index, course in enumerate(reader):
                if index in selected_courses:
                    print('Creating classroom ', index)
                    app.logger.info('Creating classroom %s', index)

                    COURSE_CONF = app.config['COURSE_CONF']

                    # Create course
                    body = {
                        'ownerId': course[COURSE_CONF['ownerId']],
                        'name': course[COURSE_CONF['name']],
                        'section': COURSE_CONF['section-format'].format(
                            *[course[val] for val in COURSE_CONF[
                                'section-values']]),
                        'courseState': 'ACTIVE'
                    }

                    try:
                        created_course = exec_classroom_creation(
                            classroom_service,
                            body)
                    except Exception as e:
                        manage_error(e, index)

                    print(created_course)
                    app.logger.info(created_course)

                    print('Adding alias to classroom ', index)
                    app.logger.info('Adding alias to classroom  %s', index)

                    alias = 'd:' + created_course['name'] + ' ' + \
                        created_course['section']
                    body = {'alias': alias}

                    alias_request = classroom_service.courses().aliases() \
                        .create(
                            body=body,
                            courseId=created_course['id']
                            )

                    try:
                        created_alias = exec_alias_creation(alias_request)
                    except Exception as e:
                        manage_error(e, index)

                    # Add teacher to course
                    teacher = {
                        'userId': course[COURSE_CONF['teacher']],
                    }

                    teacher = classroom_service.courses() \
                        .teachers().create(
                            courseId=created_course['id'],
                            body=teacher)

                    # Add teacher request to batch
                    teachers_batch.add(teacher, request_id=str(index))

                    # Merge created course and initial course infos
                    email_info = {}
                    email_info.update(course)
                    email_info.update(created_course)

                    # Give course infos to email creation
                    emails_batch.add(create_email(index, email_info, http_auth),
                        request_id=str(index))

                    # Add students to course
                    members = get_emails(
                        index,
                        http_auth,
                        course['Liste de diffusion']
                        )

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

            # Execute all batches
            try:
                exec_teacher_batch(teachers_batch, http_auth)
            except Exception as e:
                manage_error(e)
            try:
                exec_members_batch(members_batch, http_auth)
            except Exception as e:
                manage_error(e)
            try:
                emails_batch.execute(http=http_auth)
            except Exception as e:
                manage_error(e)
            # Set status of the app as free again
            process_status.creating_classrooms = False
            print('Finished creating all classrooms')
            app.logger.info('Finished creating all classrooms')


@app.route('/create', methods=['POST'])
def create():
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
