import pytest

from ldapass import ldapass


@pytest.yield_fixture(autouse=True)
def flask_app():
    ldapass.app.testing = True
    ldapass.app.debug = True
    with ldapass.app.app_context():
        yield ldapass.app


@pytest.fixture
def test_client(flask_app):
    return flask_app.test_client()


def test_get_response_code(test_client):
    '''GET / reques should return 200 HTTP code.'''
    resp = test_client.get('/')
    assert resp.status_code == 200


def test_get_html_text(test_client):
    '''GET / request should return html with proper text.'''
    resp = test_client.get('/')
    assert b'Setup/Reset LDAP Password' in resp.data


def testGetHtmlForm(test_client):
    '''GET / request should return html with proper form.'''
    resp = test_client.get('/')
    assert b'<form role="form" method="post" action="/" class="form-horizontal">' in resp.data
    assert b'<button class="btn btn-primary" type="submit">Submit</button>' in resp.data
