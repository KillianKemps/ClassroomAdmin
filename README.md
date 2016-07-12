# Classroom Admin

This application enables to create Google Classrooms in bulk from a CSV file.


## Installation

Software Requirements:
  - Docker 1.11.2
  - Docker Compose 1.7.1

To install these on Ubuntu 16.04 follow [this tutorial](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-16-04) and execute [these two command-lines](https://github.com/docker/compose/releases/tag/1.7.1)

==

API Requirements:
  - Admin SDK API enabled
  - Gmail API enabled
  - Google Classroom API enabled
  - Client ID for Web Server

To get your client ID, go on [Google's Console API](https://console.developers.google.com/apis/) and follow the wizard.

==

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
make tests
```
