## This script has been written to delete all classrooms created during tests
## while developing ClassroomAdmin

## WARNING: ALL CLASSROOMS OF THE ACCOUNT WILL BE DELETED

from __future__ import print_function
import httplib2
import os
import sys

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/classroom-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/classroom.courses'
CLIENT_SECRET_FILE = 'client_secret_old.json'
APPLICATION_NAME = 'Classroom API Python Quickstart'


def delete_courses(service, http, courses):
    def callback(request_id, response, exception):
        if exception is not None:
            print('Error deleting course "{0}": {1}'.format(
                request_id, exception))
        else:
            print('Course with id {0} deleted'.format(request_id))

    # Create batch with callback
    deletion_batch = service.new_batch_http_request(callback=callback)

    if not courses:
        print('No courses found.')
    else:
        print('Courses found:')
        for course in courses:
            print('Course: {0} | Id: {1}'.format(course['name'], course['id']))
            request = service.courses().delete(id=course['id'])
            deletion_batch.add(request, request_id=course['id'])
            print('Adding course to deletion batch...')

        print('Deleting all courses...')
        deletion_batch.execute(http=http)
        print('Batch deletion finished!\n\n')

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'classroom-python-quickstart.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def main():
    """Shows basic usage of the Classroom API.

    Creates a Classroom API service object and prints the names of the first
    10 courses the user has access to.
    """

    # Ask user for confirmation before deletion
    confirmation = input('Are you sure you want to delete all classrooms '
        'from the account? [y/N]: ')

    if confirmation is not 'Y' and confirmation is not 'y':
        print('Goodbye!')
        sys.exit()

    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('classroom', 'v1', http=http)

    fetching_courses = True
    while fetching_courses:
        print('Fetching courses...')
        results = service.courses().list(teacherId='me', pageSize=20).execute()
        courses = results.get('courses', [])

        if len(courses) > 0:
            delete_courses(service, http, courses)
        else:
            print('No more courses to delete.')
            fetching_courses = False

if __name__ == '__main__':
    main()

