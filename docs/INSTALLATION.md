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

3. Configure you app as described [in the Configuration page](CONFIGURATION.md)

4. Launch the app in background
```
cd ClassroomAdmin
docker-compose up -d
```

The app is then accessible either at `http://localhost` or at the hostname


