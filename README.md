# Classroom Admin

This application enables to create Google Classrooms in bulk from a CSV file.

## Configuration

Some setup is needed to allow you to create courses and to send emails according to your taste. This configuration allows you to choose values of your CSV file and to format some fields.

Two configuration files templates are available in `conf/`. Simply copy and rename them without `.template` to enable them.

Please see below for details about the configuration values:

### Course

Choose here the values needed among you CSV column names to create a classroom course.

```
ownerId: Owner's email or ID
name: Course name
section-format: Section template
section-values: Values for section template
teacher: Teacher email or ID
member-email-domain: Email domain of only students
```

### Email

Choose here the values to access in your CSV file and in the `course` object returned by the Google API: https://developers.google.com/classroom/reference/rest/v1/courses#Course

**Warning: You should not name your CSV columns with the same name as the keys of the `course` object. It will be overriden.**


```
to: Email to send to
subject-format: Subject template
subject-value: Value to use in subject template
content-value: Values to be used in content template
content-format: Content template
```

## Installation

Software Requirements:
  - Docker 1.11.2
  - Docker Compose 1.7.1

To install these on Ubuntu 16.04 follow [this tutorial](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-16-04) and execute [these two command-lines](https://github.com/docker/compose/releases/tag/1.7.1)

API Requirements:
  - Admin SDK API enabled
  - Gmail API enabled
  - Google Classroom API enabled
  - Client ID for Web Server

To get your client ID, go on [Google's Console API](https://console.developers.google.com/apis/) and follow the wizard.

Once the requirements installed, simply clone this directory, add your Google API secret and launch docker-compose.

Clone the repository:
``` Server
git clone https://github.com/KillianKemps/ClassroomAdmin
```

Copy your Google client ID from your computer to the server under the name `client_secret.json`
``` Computer
scp client_secret.json username@your-server-address:~/ClassroomAdmin
```

Launch the app in background
```
cd ClassroomAdmin
docker-compose up -d
```

The app is then accessible either at `http://localhost` or at the hostname

## Tests

If you want to run tests because you want to contribute do following:

Install development environment
```
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

Run tests
```
make test
```
