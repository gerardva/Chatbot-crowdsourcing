from unittest import TestCase
from urllib import request


class ServerTest(TestCase):
    def test_server_setup(self):
        # port = settings['ports']['waitress']
        # if port is None:
        port = '5000'  # try default

        result = request.urlopen('http://127.0.0.1:' + port + '/quote').read()
        self.assertIsInstance(result, bytes, "api server might be off")
