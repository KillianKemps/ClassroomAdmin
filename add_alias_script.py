## This script has been written to delete all classrooms created during tests
## while developing ClassroomAdmin

## WARNING: ALL CLASSROOMS OF THE ACCOUNT WILL BE DELETED

from __future__ import print_function
import httplib2
import os
import sys
import simplejson

from apiclient import discovery, errors
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


def add_alias_to_course(service, http, courses):
    for course in courses:
        print('{0}: {1} - {2}'.format(course['id'], course['name'],
            course['section']))
        alias = 'd:' + course['name'] + ' ' + course['section']
        body = {'alias': alias}
        # print('alias: ', alias)
        request = service.courses().aliases().create(body=body,
            courseId=course['id'])
        try:
            result = request.execute()
            print('Result: ', result)
        except errors.HttpError as e:
            error = simplejson.loads(e.content).get('error')
            if(error.get('code') == 409):
                print('Error: Classroom {0} already exist'.format(alias))
            else:
                print('Error: ', e)
                raise


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
    confirmation = input('Are you sure you want to add aliases to last 50 '
        'classrooms from the account? [y/N]: ')

    if confirmation is not 'Y' and confirmation is not 'y':
        print('Goodbye!')
        sys.exit()

    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('classroom', 'v1', http=http)

    print('Fetching courses...')
    results = service.courses().list(teacherId='me', pageSize=50).execute()
    courses = results.get('courses', [])

    add_alias_to_course(service, http, courses)

if __name__ == '__main__':
    main()
