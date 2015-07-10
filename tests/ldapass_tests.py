from ldapass import app
import unittest


class TestIndex(unittest.TestCase):

    def setUp(self):
        self.app = ldapass.app.test_client()
        self.resp = self.app.get('/')

    def tearDown(self):
        pass

    def testGetResponseCode(self):
        '''GET / reques should return 200 HTTP code.'''
        self.assertEqual(self.resp.status_code, 200)

    def testGetHtmlText(self):
        '''GET / request should return html with proper text.'''
        self.assertIn(
                    b'Setup/Reset LDAP Password',
                    self.resp.data)

    def testGetHtmlForm(self):
        '''GET / request should return html with proper form.'''
        self.assertIn(
            b'<form role="form" method="post" action="/"'
            b' class="form-horizontal">',
            self.resp.data)
        self.assertIn(
            b'<button class="btn btn-primary" type="submit">Submit</button>',
            self.resp.data)

if __name__ == '__main__':
    unittest.main()
