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
        with self.subTest(4):
            self.post_type_3_task()
        with self.subTest(5):
            self.post_task_with_option_answer()

    def create_new_user(self):
        r = requests.get('http://localhost:5000/worker/users')

        print(r.text)
        r_as_json = json.loads(r.text)
        self.userId = r_as_json['userId']

    def post_task(self):
        r = requests.post('http://localhost:5000/requester/tasks', data=json.dumps({
            'userId': self.userId,
            'description': 'Annotation of receipts',
            'content': [
                {'data': {'pictureUrl': 'https://upload.wikimedia.org/wikipedia/commons/0/0b/ReceiptSwiss.jpg'}}
            ],
            'questionRows': [
                {'question': 'What company is this receipt from?',
                 'answerSpecification': {'type': 'plaintext'}},
                {'question': 'What is the address of this company?',
                 'answerSpecification': {'type': 'plaintext'}}
            ]
        }))

        print(r.text)

    def post_type_3_task(self):
        r = requests.post('http://localhost:5000/requester/tasks', data=json.dumps({
            'userId': self.userId,
            'description': 'Taking picture of landmark',
            'content': [
                {'location': {'longitude': 52.007545,
                              'latitude': 4.3565297}, }
            ],
            'questionRows': [
                {'question': 'Please take a picture of Delft station.',
                 'answerType': 'image'},
                {'question': 'Please walk to the bike cellar. How many available bike spaces are there, according to the signs?',
                 'answerType': 'plaintext'}
            ]
        }))

        print(r.text)

    def post_task_with_option_answer(self):
        r = requests.post('http://localhost:5000/requester/tasks', data=json.dumps({
            'userId': self.userId,
            'description': 'annotation of receipts',
            'dataLocation': {'longitude': 0.0,
                             'latitude': 0.0},
            'data': [
                {'pictureUrl': 'https://upload.wikimedia.org/wikipedia/commons/0/0b/ReceiptSwiss.jpg'}
            ],
            'questionRows': [
                {'question': 'What company is this receipt from?',
                 'answerSpecification': {'type': 'option',
                                         'options': ['Albert Heijn', 'HEMA', 'Flying Tiger']}},
            ]
        }))

        print(r.text)

    def get_task(self):
        r = requests.get('http://localhost:5000/worker/tasks?order=random&limit=1')

        print(r.text)
        r_as_json = json.loads(r.text)[0]
        self.contentId = r_as_json['contentId']
        self.questionId = r_as_json['questions'][0]['questionId']

    def post_answer(self):
        print('userId: ' + str(self.userId))
        print('contentId: ' + str(self.contentId))
        print('questionId: ' + str(self.questionId))

        r = requests.post('http://localhost:5000/worker/answers', data=json.dumps({
            'userId': self.userId,
            'contentId': self.contentId,
            'questionId': self.questionId,
            'answer': 'Berghotel Grosse Scheidegg'
        }))

        print(r.text)
