import unittest
import random

from classroom_admin import app


class TestBase(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.client = self.app.test_client()

    def tearDown(self):
        del self.app

    def test_config(self):
        assert self.app.config['ASSETS_DEBUG'] == True
        assert self.app.config['UPLOAD_FOLDER'] == 'uploads/'
        assert self.app.config['ALLOWED_EXTENSIONS'] == set(['csv'])


if __name__ == '__main__':
    unittest.main()
