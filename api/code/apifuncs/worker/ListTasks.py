import json
from apiserver import Task

class ListTasksResource:
	def on_get(self, req, resp):
		"""Handles GET requests"""
		
		result = {
			'tasks': []
		}
		
		for task in Task.select():
			result['tasks'].append(task.taskId) 

		resp.body = json.dumps(result)