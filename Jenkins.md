# Setup of a Jenkins server

## Installing Jenkins

The following explains how to set up a Jenkins server on Ubuntu 20.04.

First you need a Java 11 environment:

```bash
sudo apt-get install openjdk-11-jdk openjdk-11-jdk-headless
```

Then, configure Jenkins repository and install it:

```bash
wget -q -O - https://pkg.jenkins.io/debian-stable/jenkins.io.key | sudo apt-key add -
sudo sh -c 'echo deb https://pkg.jenkins.io/debian-stable binary/ > \
    /etc/apt/sources.list.d/jenkins.list'
sudo apt-get update
sudo apt-get install jenkins
```

By default, Jenkins server tries to start on port 8080. If this port is already in use by another service, the port can 
be changed by updating the following file `/etc/default/jenkins`. We set the port to 8081.

The Jenkins server is started at startup.

## Setup of reverse proxy

If you are using a reverse proxy like NGINX, you can add the following to the configuration file:

```text
server {
    # only listen to https here
    listen                          443 ssl http2;
    listen                          [::]:443 ssl http2;
    server_name                     jenkins.kango.ovh;

    access_log                      /var/log/nginx/jenkins.kango.ovh.access.log;
    error_log                       /var/log/nginx/jenkins.kango.ovh.error.log;

    location / {
        proxy_pass                  http://localhost:8081;
        proxy_set_header            Host $host;
        proxy_set_header            X-Real-IP $remote_addr;
        proxy_http_version          1.1;

        proxy_set_header            X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header            X-Forwarded-Proto http;
        proxy_redirect              http:// $scheme://;
    }
}
```

Finally, use `certbot`:

```bash
sudo certbot --nginx
```

This will set up the https redirection and the SSL certificates in the NGINX configuration file.

## Configuration of Jenkins

### Jenkins server

During the first log into the Jenkins system, install the recommended plugins. Then the following plugins may be 
installed:

- Embeddable Build Status Plugin
- Parameterized Trigger plugin

### GitHub repository

Add a webhook to your GitHub repository settings pointing to the Jenkins server 
(in this example https://jenkins.kango.ovh) followed by `/github-webhook`. The full url shall look like this one:

```text
https://jenkins.kango.ovh//github-webhook/
```

Then, select content type as `application/json`.

Finally, select `Let me select individual events` and check `Pushes` and `Pull requests`.

### Jenkins build

Create a build with the following minimum settings:

- In the source code management section select git and provide the path to the repository on GitHub
- In what triggers build section, select `GitHub hook trigger for GITScm polling`. You can select which branches are 
  monitored, leave blank for all branches.
- In build environment section, you can check `Delete workspace before build starts`
- In the build section, simply add a shell script with the following command:

```bash
make jenkins
```

Once the build configuration is completed, you can go to the `Embeddable Build Status` menu of the build and 
copy/paste the shield into the README.md file.

