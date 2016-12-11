import argparse
import datetime
import os
import smtplib
import sqlite3
import time
import uuid

from ConfigParser import RawConfigParser
from email.mime.text import MIMEText
from flask import Flask, flash, request, render_template, redirect, url_for
import ldap
from wtforms import Form, TextField, PasswordField, validators


app = Flask(__name__)
app.secret_key = os.urandom(128)
conf = RawConfigParser()
conf.read(os.environ['LDAPASS_CONFIG'])


class EmailForm(Form):
    mail = TextField('Email address', [
        validators.Required(),
        validators.Length(min=5, max=250),
        validators.Email()
    ])


class PasswordForm(Form):
    passwd = PasswordField('New password', [
        validators.Required(),
        validators.EqualTo('passwd_confirm', message='Passwords must match')
    ])
    passwd_confirm = PasswordField('Confirm new password')


def parse_arguments(description):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-c', action="store", dest="conf_file", required=True)
    return parser.parse_args()


def send_mail(mail, reset_url):
    msg = MIMEText(
        '''
        Hi,
        Your LDAP password reset link is:
        {reset_url}
        This url will be valid for next 24 hours. In case of any issues, \
        please, get in touch with someone from LDAP administration.
        '''.format(reset_url=reset_url))
    msg['Subject'] = 'LDAP password reset link'
    msg['To'] = mail
    msg['From'] = 'noreply@nodomain.com'
    s = smtplib.SMTP(conf.get('app', 'smtp_addr'))
    s.sendmail(msg['From'], msg['To'], msg.as_string())
    s.quit()


@app.route('/', methods=['GET', 'POST'])
def index():
    error = None
    form = EmailForm(request.form)
    if request.method == 'GET':
        return render_template('index.html', error=error, form=form)

    elif request.method == 'POST':
        if form.validate():
            ldap_uri = 'ldap://{addr}:{port}'.format(
                addr=conf.get('ldap', 'addr'), port=conf.get('ldap', 'port'))
            ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
            ldap_conn = ldap.initialize(ldap_uri, trace_level=conf.get('ldap', 'debug'))
            try:
                ldap_conn.start_tls_s()
            except ldap.LDAPError as error:
                return render_template('index.html', error=error, form=form)
            try:
                search_filter = 'mail={mail}'.format(mail=form.mail.data)
                ldap_result_id = ldap_conn.search(
                    conf.get('ldap', 'basedn'), ldap.SCOPE_SUBTREE,
                    search_filter, None)
            except ldap.LDAPError as error:
                return render_template('index.html', error=error, form=form)
            result_type, result_data = ldap_conn.result(ldap_result_id, 0)
            if len(result_data) == 1:
                link_id = '{uuid}-{account}'.format(
                    uuid=str(uuid.uuid4()),
                    account=form.mail.data.split('@')[0]
                )

                db_conn = sqlite3.connect(conf.get('app', 'database'))
                db_curs = db_conn.cursor()
                db_curs.execute(
                    "SELECT id FROM mails WHERE mail='{mail}'".format(
                        mail=form.mail.data))
                db_data = db_curs.fetchall()
                if len(db_data) == 0:
                    db_curs.execute(
                        "INSERT INTO mails (mail, link_id, created) VALUES \
                        ('{mail}', '{link_id}', '{created}')".format(
                            mail=form.mail.data,
                            link_id=link_id,
                            created=datetime.datetime.now()
                        ))
                    flash('Email containing password reset url has been sent \
                        to {mail}'.format(mail=form.mail.data))
                else:
                    db_curs.execute(
                        "DELETE FROM mails WHERE mail='{mail}'".format(
                            mail=form.mail.data))
                    db_curs.execute(
                        "REPLACE INTO mails (mail, link_id, created) VALUES \
                        ('{mail}', '{link_id}', '{created}')".format(
                            mail=form.mail.data,
                            link_id=link_id,
                            created=datetime.datetime.now()
                        ))
                    flash('Email containing password reset url has been sent \
                        to {mail}. Previous reset urls have been \
                        invalidated.'.format(mail=form.mail.data))
                db_conn.commit()
                db_conn.close()

                reset_url = 'http://{hostname}:{port}/reset/{link_id}'.format(
                    hostname=conf.get('app', 'hostname'),
                    port=conf.get('app', 'listen_port'),
                    link_id=link_id
                )
                send_mail(form.mail.data, reset_url)
            elif len(result_data) > 1:
                error = 'More than one user found with email address of \
                    {mail}. Plese, get in touch with LDAP administration \
                    team.'.format(mail=form.mail.data)
            else:
                error = 'No user found with email address of {mail}. Plese, \
                    get in touch with LDAP administration.'.format(
                    mail=form.mail.data)
            return render_template('index.html', error=error, form=form)

        else:
            error = 'The mail address you have filled is invalid.'
            return render_template('index.html', error=error, form=form)


@app.route('/reset/<link_id>', methods=['GET', 'POST'])
def reset(link_id):
    error = None
    form = PasswordForm(request.form)

    db_conn = sqlite3.connect(conf.get('app', 'database'))
    db_curs = db_conn.cursor()
    db_curs.execute("SELECT * FROM mails WHERE link_id='{link_id}'".format(
        link_id=link_id))
    db_data = db_curs.fetchall()

    if len(db_data) == 1:
        if request.method == 'GET':
            flash(
                'You are changing password for the account of {mail}'.format(
                    mail=db_data[0][1]))
            return render_template(
                'reset.html',
                error=error,
                form=form,
                link_id=link_id)

        if request.method == 'POST':
            if form.validate():
                ldap_uri = 'ldap://{addr}:{port}'.format(
                    addr=conf.get('ldap', 'addr'),
                    port=conf.get('ldap', 'port')
                )
                ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
                ldap_conn = ldap.initialize(ldap_uri, trace_level=conf.get('ldap', 'debug'))
                try:
                    ldap_conn.start_tls_s()
                except ldap.LDAPError as error:
                    return render_template('error.html', error=error)
                try:
                    search_filter = 'mail={mail}'.format(mail=db_data[0][1])
                    ldap_result_id = ldap_conn.search(
                        conf.get('ldap', 'basedn'),
                        ldap.SCOPE_SUBTREE,
                        search_filter,
                        None)
                    result_type, result_data = ldap_conn.result(ldap_result_id, 0)
                    ldap_conn.simple_bind_s(
                        conf.get('ldap', 'user'), conf.get('ldap', 'pass'))
                    ldap_conn.passwd_s(
                        'uid={uid},{basedn}'.format(
                            uid=result_data[0][1]['uid'][0],
                            basedn=conf.get('ldap', 'basedn')),
                        None,
                        '{passwd}'.format(passwd=form.passwd.data))
                except ldap.LDAPError as error:
                    error = 'LDAP error: {error}, please get in touch with \
                        LDAP administration.'.format(error=error)
                    return render_template(
                        'reset.html',
                        error=error,
                        form=form
                    )
                flash('Password for account {mail} has been changed.'.format(
                    mail=db_data[0][1]))
                db_curs.execute(
                    "DELETE FROM mails WHERE link_id='{link_id}'".format(
                        link_id=link_id))
                db_conn.commit()
                db_conn.close()
                return redirect(url_for('index'))
            else:
                error = 'The form is invalid, please try again.'
                return render_template('reset.html', error=error, form=form)
    else:
        db_conn.close()
        error = 'There is no such password reset id {link_id}'.format(
            link_id=link_id)
        return render_template('error.html', error=error)


if __name__ == '__main__':
    conf = RawConfigParser()
    conf.read(os.environ['LDAPASS_CONFIG'])

    # test if the database exists, and create it if not, with proper warning
    db_conn = sqlite3.connect(conf.get('app', 'database'))
    db_curs = db_conn.cursor()
    db_curs.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='mails'")
    if not db_curs.fetchall():
        print('WARNING: the SQLite file {database} doesnt exist! Sleeping for \
            10 seconds and creating the database file. KILL ME if this is an \
            error!').format(database=conf.get('app', 'database'))
        time.sleep(10)
        db_curs.execute(
            '''create table mails (
                id      INTEGER PRIMARY KEY,
                mail    VARCHAR(255) NOT NULL COLLATE NOCASE,
                link_id VARCHAR(512) NOT NULL COLLATE NOCASE,
                created INTEGER DEFAULT NULL);
            ''')
        db_conn.commit()
        print('Created the sqlite file.')
    else:
        print('SQLite file {database} found.').format(
            database=conf.get('app', 'database'))
    db_conn.close()

    app.run(host=conf.get('app', 'listen_addr'),
            port=conf.getint('app', 'listen_port'),
            debug=conf.getboolean('app', 'debug'))
