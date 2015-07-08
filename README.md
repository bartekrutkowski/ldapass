ldapass [![Build Status](https://travis-ci.org/bartekrutkowski/ldapass.png?branch=master)](https://travis-ci.org/bartekrutkowski/ldapass)
=======
**Web application for setting/changing LDAP user passwords.**

LDAPass is a Python/Flask simple web application that aims to make Unix/Linux LDAP user account passwords manageable by their users without involvement of DevOps/SysAdmin resources in a simple, non complicated application not requiring extensive setup nor maintenance.

## Requirements

To host LDAPass on a Unix/Linux system you need the following software installed:

- Python 2.7.x with following modules:
  - Flask
  - python-ldap
  - WTForms
- A web server (Nginx, Apache etc., example Nginx configuration is provided)
- UWSGI 2.x

## Installation

The following examples are assuming you are deploying LDAPass on a FreeBSD system, you should adjust your paths accordingly to your OS.

Clone the repository into proper location:

```sh
$ git clone git@github.com:bartekrutkowski/ldapass.git /var/www/ldapass
```
