import json
from unittest import TestCase

import requests


class ApiIntegrationTest(TestCase):
    userId = -1
    contentId = -1
    questionId = -1

    def test_api(self):
        with self.subTest(0):
            self.create_new_user()
        with self.subTest(1):
            self.post_task()
        with self.subTest(2):
            self.get_task()
        with self.subTest(3):
            self.post_answer()

    def create_new_user(self):
        r = requests.get('http://localhost:5000/worker/createNewUser')

        print(r.text)
        r_as_json = json.loads(r.text)
        self.userId = r_as_json['userId']

    def post_task(self):
        r = requests.post('http://localhost:5000/requester/inputTask', data=json.dumps({
            'userId': self.userId,
            'data': [
                {'pictureUrl': 'someUrl'}
            ],
            'questionRows': {
                'q1': 'what location',
                'q2': 'other q'
            }
        }))

        print(r.text)

    def get_task(self):
        r = requests.get('http://localhost:5000/worker/getRandomJob')

        print(r.text)
        r_as_json = json.loads(r.text)
        self.contentId = r_as_json['contentId']
        self.questionId = r_as_json['questions'][0]['questionId']

    def post_answer(self):
        r = requests.post('http://localhost:5000/worker/submitAnswer', data=json.dumps({
            'userId': self.userId,
            'contentId': self.contentId,
            'questionId': self.questionId,
            'answer': 'this is truly a legit answer'
        }))

        print(r.text)
