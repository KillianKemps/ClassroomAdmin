# Classroom Admin

This application enables to create Google Classrooms in bulk from a CSV file when you are using the Google Apps suite for your organization.

The problem encountered by the [Web School Factory](https://www.webschoolfactory.fr/) Staff was that they had to create
each Google Classroom and add each student to it manually. They had to do it every year for each class. This is quite a repetitive task.

So, we developed Classroom Admin which allows the staff of a school to create all classrooms and affect to them students all in one stretch.

In order to use the software, the Staff has to prepare CSV (or Excel) files with the list of all courses
with for each of them the email of the teacher and the mailing list of the students.
Then, they only need to upload it into the Classroom Admin interface and click on the "Create courses" button. And voilà! Each Google Classroom will be created with students automatically added to it and the teachers will receive an email with all the information they need to manage their classroom.

In case some teacher tells you something like *"Where is my Google Classroom? I don't know where I have to put my classroom materials!"*, there is also a feature which allows you to resend the email with all the information for given courses. You just need to upload the right CSV file, select the courses for which you want to resend and click on "Resend emails manually".

This feature has also been added for technical reasons because Gmail can't guarantee that all emails are sent accordingly and you may need to resend the emails in case Gmail has not been able to process everything.

![Classroom Admin Screenshot](classroom_admin_screenshot.png)

## Documentation

- [Installation](docs/INSTALLATION.md)
- [Configuration](docs/CONFIGURATION.md)
- [Developers](docs/DEVELOPERS.md)
- [License](LICENSE.md)

Made by a student of the [Web School Factory](https://www.webschoolfactory.fr/).

[!["Web School Factory"](webschoolfactory_0.png)](https://www.webschoolfactory.fr/)
