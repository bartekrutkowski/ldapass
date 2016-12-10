ldapass [![Build Status](https://travis-ci.org/bartekrutkowski/ldapass.svg?branch=master)](https://travis-ci.org/bartekrutkowski/ldapass)
=======
**Web application for setting/changing LDAP user passwords.**

LDAPass is a Python/Flask simple web application that aims to make Unix/Linux user account LDAP passwords manageable by their owners without involvement of DevOps/SysAdmin resources in a simple application not requiring extensive setup or maintenance.

## Requirements

To run LDAPass on a Unix/Linux system you need the following software installed:

- Python 2.7.x with following modules installed:
  - Flask
  - Python-LDAP
  - WTForms
  - SQLite3
- A web server (Nginx, Apache etc., example Nginx configuration is provided)
- Application Server Container (example UWSGI 2.x configuration is provided)

## Installation

The following examples are assuming you are deploying LDAPass on a FreeBSD system, you should adjust your paths accordingly to your OS.

Clone the repository to the chosen location:

```sh
$ git clone https://github.com/bartekrutkowski/ldapass.git /var/www/ldapass
```

Copy the example ldapass.conf configuration file to main app directory and edit it with appropriate values:

```sh
$ cp /var/www/ldapass/examples/ldapass.conf /var/www/ldapass/ldapass/ldapass.conf
$ vi /var/www/ldapass/ldapass/ldapass.conf
```

Copy the Nginx nginx_ldapass.example.com.conf configuration file into your OS Nginx config directory and edit it with appropriate values:

```sh
$ cp /var/www/ldapass/examples/nginx_ldapass.example.com.conf /usr/local/etc/nginx/conf.d/ldapass.example.com.conf
$ vi /usr/local/etc/nginx/conf.d/ldapass.example.com.conf
```

Copy the UWSGI uwsgi_ldapass.ini configuration file into your OR UWSGI config directory and edit it with appropriate values:

```sh
$ cp /var/www/ldapass/examples/uwsgi_ldapass.ini /usr/local/etc/uwsgi_ldapass.ini
$ vi /usr/local/etc/uwsgi_ldapass.ini
```

Start the UWSGI and Nginx services:

```sh
$ service uwsgi start
$ service nginx start
```

You're done!
