import json

class GetRandomTaskResource:
	def on_get(self, req, resp):
		"""Handles GET requests"""
		randomTask = {
			'taskId': 1,
			'dataId': 1,
			'dataRow': {'pictureUrl': 'http://thisisanimage.com'},
			'questionRows': [
				{'show Location': '$$IMG($pictureUrl)'},
				{'location question': '$$RESULTWhat city is this picture off?'}
			]
		}

		resp.body = json.dumps(randomTask)