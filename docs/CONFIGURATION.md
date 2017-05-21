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
