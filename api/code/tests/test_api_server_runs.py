#!/usr/bin/python
import unittest
from urllib import request

from api.code.settings import settings


class ApiServerRunningTestCase(unittest.TestCase):
    def runTest(self):
        port = settings['ports']['waitress']
        if port is None:
            port = '5000'  # try default

        result = request.urlopen('http://127.0.0.1:' + port + '/quote').read()
        self.assertIsInstance(result, str, "api server might be off")
