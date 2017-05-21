# Classroom Admin

This application enables to create Google Classrooms in bulk from a CSV file when you are using the Google Apps suite for your organization.

The problem encountered by the Web School Factory Staff was that they had to create
each Google Classroom and add each student to it manually. They had to do it every year for each class. This is quite a repetitive task.

So, we developed Classroom Admin which allows the staff of a school to create all classrooms and affect to them students all in one stretch.

In order to use the software, the Staff has to prepare CSV (or Excel) files with the list of all courses
with for each of them the email of the teacher and the mailing list of the students.
Then, they only need to upload it into the Classroom Admin interface and click on the "Create courses" button. And voilà! Each Google Classroom will be created with students automatically added to it and the teachers will receive an email with all the information they need to manage their classroom.

In case some teacher tells you something like *"Where is my Google Classroom? I don't know where I have to put my classroom materials!"*, there is also a feature which allows you to resend the email with all the information for given courses. You just need to upload the right CSV file, select the courses for which you want to resend and click on "Resend manually emails".

This feature has also been added for technical reasons because Gmail can't guarantee that all emails are sent accordingly and you may need to resend the emails in case Gmail has not been able to process everything.

![Classroom Admin Screenshot](classroom_admin_screenshot.png)

## Installation

### Requirements

Software Requirements:
  - Docker 1.11.2
  - Docker Compose 1.7.1

To install these on Ubuntu 16.04 follow [this tutorial](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-16-04) and execute [these two command-lines](https://github.com/docker/compose/releases/tag/1.7.1)

API Requirements:
  - Admin SDK API enabled
  - Gmail API enabled
  - Google Classroom API enabled
  - Client ID for Web Server

### Google's admin account creation

To get your client ID, go on [Google's Console API](https://console.developers.google.com/apis/).

1. Create a Project with the name of your choice
2. Create keys for your project
  1. Choose Web Application keys
  2. Download the client ID and the client secret JSON file given by Google and
  rename it to `client_secret.json`
  3. Authorize the domain name where you want to host the app
3. Enable the three following APIs for the project:
  1. Admin SDK API
  2. Gmail API
  3. Google Classroom API

### Application setup

Once the requirements installed, simply clone this directory on your server,
add your Google API secret and launch docker-compose:

1. Clone the repository:
``` Server
git clone https://github.com/KillianKemps/ClassroomAdmin
```

2. Copy your Google client ID from your computer to the server under the name `client_secret.json`
``` Computer
scp client_secret.json username@your-server-address:~/ClassroomAdmin
```

3. Configure you app as described [below](#Configuration)

4. Launch the app in background
```
cd ClassroomAdmin
docker-compose up -d
```

The app is then accessible either at `http://localhost` or at the hostname

## Configuration

Some setup is needed to allow you to create courses and to send emails according to your taste. This configuration allows you to choose values of your CSV file and to format some fields.

**This is needed because the Classroom Admin application needs to know which fields to use from your CSV file and how to use them.**

You can see an example of CSV file in the [example](example/courses.csv) folder.

Two configuration files templates are available in `conf/`. Simply copy and rename them without `.template` to enable them.

Please see below for details about the configuration values:

### Course

A Google Classroom needs the following fields to be created:
1. OwnerId
2. Name
3. Section
4. Teacher
5. Students email

You will need to **map** the following fields with your CSV file column names

For the `section-values` field you will need to give a list of your CSV file column names.

And you will need to format these values in the `section-format` field using
them with the `{x}` syntax where `x` is the value position in the list.

```
ownerId: Owner's email or ID
name: Course name
section-values: Values for section template
section-format: Section template
teacher: Teacher email or ID
member-email-domain: Email domain of only students
```

*Example of a course template:*
```
ownerId: Owner
name: Name
section-values:
  - Year
  - Domain
  - Promotion
section-format: '{0} - {1} - {2}'
teacher: Teacher Email
students: Students email
member-email-domain: '@my-school.com'
```

*Which will create this kind of courses:*
```
Name: 'Math'
Owner: 'administration@my-school.com'
Section: '2017 - Science - Promotion 2018'
Teacher: 'theteacher@my-school.com'
Students: 'all-2018-students@my-school.com'
```

### Email

To send a Gmail email, we need the following fields:
1. To (address to send to)
2. Subject (subject of the email)
3. Content (content of the email)

You will need to map the following fields with fields you have in your CSV file.

You may also want to use fields given by Google in the `course` object returned by the Google API: https://developers.google.com/classroom/reference/rest/v1/courses#Course

**Warning: You should not name your CSV columns with the same name as the keys of the `course` object. It will be overriden.**


In the fields finishing with `-value` you will need to give a list of your CSV fields to be used and values given by Google's API.
In the fields finishing with `-format` you will format the values given previously by naming them with `{x}` where `x` is the value position in the list.
```
to: Email to send to
subject-value: Value to use in subject template
subject-format: Subject template
content-value: Values to be used in content template
content-format: Content template
```

*Example of an email template:*
```
to: Teacher Email
subject-value: Course Name
subject-format: 'Subject: {0}'
content-value:
  - Surname
  - Name
  - alternateLink
  - enrollmentCode
  - Teacher Email
content-format:
  >
    <html>
    <p>Hello {0} {1},</p>

    <p>You can access the created course at {2}</p>

    <p>You can also give access to the students by giving them the following enrollment code: {3}</p>

    <p><span style="font-weight:bold; color:red">CAUTION,</span> this interface is only accessible through the email the school gave you: {4}</p>

    <p>The School team</p>
    </html>
```
Where the following values may be given from your CSV file:
  - Teacher Email
  - Course Name
  - Surname
  - Name

And where the following values are given by Google's API:
  - alternateLink
  - enrollmentCode

*Which may send this kind of email:*
```
To: john.teacher@my-school.com
Subject: Subject: Math
Content:
  >
    <html>
    <p>Hello John Doe,</p>

    <p>You can access the created course at https://classroom.google.com/fake-classroom</p>

    <p>You can also give access to the students by giving them the following enrollment code: 0123abc</p>

    <p><span style="font-weight:bold; color:red">CAUTION,</span> this interface is only accessible through the email the school gave you: john.teacher@my-school.com</p>

    <p>The School team</p>
    </html>
```


## Tests

You are a developer and want to contribute?
If you want to run tests do the following:

Install the development environment
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
