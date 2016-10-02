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
from ..utils import process_status, manage_error


# Create email object
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

    try:
        message = service.users().messages().send(userId='me', body=body)
    except Exception as e:
        manage_error(e)

    return message

# Callback function for emails sent to teachers
def email_callback(request_id, response, exception):
    if exception is not None:
        error = simplejson.loads(exception.content).get('error')
        print('An error occurred while sending email to course of index {0}: \
            {1}'.format(request_id, error))
        app.logger.error('An error occurred while sending email to course of \
            index {0}: {1}'.format(request_id, error))


def send_emails_created_classrooms(selected_courses, credentials):
    # Set status of the app as being busy
    process_status.creating_classrooms = True
    http_auth = credentials.authorize(httplib2.Http())
    classroom_service = discovery.build('classroom', 'v1', http=http_auth)
    email_service = discovery.build('gmail', 'v1', http=http_auth)
    filename = os.path.join(app.config['UPLOAD_FOLDER'], 'courses_list.csv')

    if os.path.isfile(filename) :
        with open(filename) as csvfile:
            reader = csv.DictReader(csvfile)

            # Create batch for email requests
            emails_batch = email_service.new_batch_http_request(
                callback=email_callback)

            # Enumerate in courses from CSV
            for index, course in enumerate(reader):
                if index in selected_courses:
                    COURSE_CONF = app.config['COURSE_CONF']

                    # Course body
                    body = {
                        'ownerId': course[COURSE_CONF['ownerId']],
                        'name': course[COURSE_CONF['name']],
                        'section': COURSE_CONF['section-format'].format(
                            *[course[val] for val in COURSE_CONF[
                                'section-values']]),
                        'courseState': 'ACTIVE'
                    }

                    alias = 'd:' + body['name'] + ' ' + body['section']
                    created_course = classroom_service.courses().get(id=alias)\
                        .execute()

                    # Merge created course and initial course infos
                    email_info = {}
                    email_info.update(course)
                    email_info.update(created_course)

                    email_request_id = str(index)
                    # Give course infos to email creation
                    emails_batch.add(create_email(email_info, http_auth),
                        request_id=email_request_id)

            try:
                emails_batch.execute(http=http_auth)
            except Exception as e:
                manage_error(e)
            # Set status of the app as free again
            process_status.sending_emails = False
            print('Finished sending all emails')
            app.logger.info('Finished sending all emails')


@app.route('/manually-send-email', methods=['POST'])
def manually_send_email():
    print('Preparing to send emails for classrooms')
    app.logger.info('Preparing to send emails for classrooms')

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
            target=send_emails_created_classrooms,
            args=(selected_courses, credentials)).start()
        return render_template('success.html'), 202
