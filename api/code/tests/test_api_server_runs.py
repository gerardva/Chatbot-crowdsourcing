#!/usr/bin/python
import urllib2
import unittest
from code.settings import settings

class ApiServerRunningTestCase(unittest.TestCase):
	def runTest(self):
		port = settings['ports']['waitress']
		if port is None:
			port = '8080' # try default
		
		result = urllib2.urlopen('http://127.0.0.1:' + port + '/quote').read()
		self.assertIsInstance(result, str, "api server might be off")
