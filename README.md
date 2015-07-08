ldapass [![Build Status](https://travis-ci.org/bartekrutkowski/ldapass.png?branch=master)](https://travis-ci.org/bartekrutkowski/ldapass)
=======
**Web application for setting/changing LDAP user passwords.**

LDAPass is a Python/Flask simple web application that aims to make Unix/Linux LDAP user account passwords manageable by their users without involvement of DevOps/SysAdmin resources in a simple, non complicated application not requiring extensive setup nor maintenance.

## Requirements

To host LDAPass you need the following software installed:

- Python 2.7.x and following modules:
  - Flask
  - python-ldap
  - WTForms
  - Werkzeug
- A web server (Nginx, Apache etc., example Nginx configuration is probvided)
- UWSGI 2.x
