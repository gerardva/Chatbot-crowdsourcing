from api.code.model import *
from pipelines.reviewPipeline import *
import json
import unittest
import requests

# TODO this should be imported form settings
WAITRESS_PORT = 5000
base_api_url = 'http://localhost:'+str(WAITRESS_PORT)


class ApiIntegrationTest(unittest.TestCase):
    userId = -1
    contentId = -1
    questionId = -1

    def test_api(self):
        tests = [
            self.create_new_user,
            self.post_task,
            self.get_task,
            self.get_location_based_task,
            self.post_answer,
            self.post_type_3_task,
            self.post_task_with_option_answer,
            self.can_not_answer_content,
            self.make_review_pipeline,
        ]

        for test_func in tests:
            with self.subTest(name=test_func.__name__):
                test_func()

    def create_new_user(self):
        r = requests.post(base_api_url + '/worker/users', data=json.dumps({
            'facebookId': 'this is totally a legit facebook id'
        }))

        print('returned user json: ' + r.text)
        r_as_json = json.loads(r.text)
        self.userId = r_as_json['userId']

    def post_task(self):
        r = requests.post(base_api_url + '/requester/tasks', data=json.dumps({
            'userId': self.userId,
            'description': 'Annotation of receipts',
            'content': [
                {'data': {'pictureUrl': 'https://upload.wikimedia.org/wikipedia/commons/0/0b/ReceiptSwiss.jpg'}},
                {'data': {'pictureUrl': 'second content url'}}
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
        r = requests.post(base_api_url + '/requester/tasks', data=json.dumps({
            'userId': self.userId,
            'description': 'Taking picture of landmark',
            'content': [
                {'location': {'longitude': 52.007545,
                              'latitude': 4.3565297}, }
            ],
            'questionRows': [
                {'question': 'Please take a picture of Delft station.',
                 'answerSpecification': {'type': 'image'}},
                {'question': 'Please walk to the bike cellar. How many available bike spaces are there, according to the signs?',
                 'answerSpecification': {'type': 'plaintext'}}
            ]
        }))

        print(r.text)

    def post_task_with_option_answer(self):
        r = requests.post(base_api_url + '/requester/tasks', data=json.dumps({
            'userId': self.userId,
            'description': 'annotation of receipts',
            'dataLocation': {'longitude': 0.0,
                             'latitude': 0.0},
            'content': [
                {'data': {'pictureUrl': 'https://upload.wikimedia.org/wikipedia/commons/0/0b/ReceiptSwiss.jpg'}}
            ],
            'questionRows': [
                {'question': 'What company is this receipt from?',
                 'answerSpecification': {'type': 'option',
                                         'options': ['Albert Heijn', 'HEMA', 'Flying Tiger']}},
            ]
        }))

        print(r.text)

    def get_task(self):
        r = requests.get(base_api_url + '/worker/' + str(self.userId) + '/tasks?order=random&limit=1')

        print("get_task: " + r.text)
        r_as_json = r.json()[0]
        self.contentId = r_as_json['contentId']
        self.questionId = r_as_json['questions'][0]['questionId']

    def get_location_based_task(self):
        r = requests.get(base_api_url + '/worker/tasks?order=location&longitude=1.0&latitude=1.0&range=1.0&limit=10')

        print('location based task: '+r.text)
        #r_as_json = json.loads(r.text)[0]
        #self.contentId = r_as_json['contentId']
        #self.questionId = r_as_json['questions'][0]['questionId']

    def post_answer(self):
        print('userId: ' + str(self.userId))
        print('contentId: ' + str(self.contentId))
        print('questionId: ' + str(self.questionId))

        r = requests.post(base_api_url + '/worker/answers', data=json.dumps({
            'userId': self.userId,
            'contentId': self.contentId,
            'questionId': self.questionId,
            'answer': 'Berghotel Grosse Scheidegg'
        }))

        print(r.text)

    def can_not_answer_content(self):
        r = requests.post(base_api_url + '/worker/users', json.dumps({
            'facebookId': 'legit id 2'
        }))

        r_as_json = json.loads(r.text)

        other_user_id = r_as_json['userId']

        r = requests.post(base_api_url + '/requester/tasks', data=json.dumps({
            'userId': other_user_id,
            'description': 'Annotation of receipts',
            'canNotMake': [
                [other_user_id]
            ],
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

        r_as_json = json.loads(r.text)

        task_id = r_as_json['taskId']
        self.task_id = task_id
        print('\nlooking for taskid '+str(task_id)+'\n')

        r = requests.get(base_api_url + '/worker/' + str(other_user_id) + '/tasks?order=random')

        r_as_json = json.loads(r.text)
        found_task = False

        print('\ncan_not_answer_tasks: '+str(len(r_as_json))+'\n')

        for task in r_as_json:
            if task['taskId'] == task_id:
                found_task = True

        self.assertFalse(found_task,
                             'found a task (with just one content) that should have been blocked by CanNotAnswer')

    def make_review_pipeline(self):
        r = requests.post(base_api_url + '/worker/users', json.dumps({
            'facebookId': 'legit id 2'
        }))

        r_as_json = json.loads(r.text)

        other_user_id = r_as_json['userId']

        # r = requests.get('http://localhost:5000/requester/tasks?taskId='+str(self.task_id))
        #
        # r_as_json = json.loads(r.text)

        content_id = Content.get(Content.task == self.task_id).id
        questions = Question.select().where(Question.task == self.task_id)

        r = requests.post(base_api_url + '/worker/' + str(other_user_id) + '/answers', data=json.dumps({
            'userId': other_user_id,
            'contentId': content_id,
            'questionId': questions[0].id,
            'answer': 'Berghotel Grosse Scheidegg'
        }))

        r = requests.post(base_api_url + '/worker/' + str(other_user_id) + '/answers', data=json.dumps({
            'userId': other_user_id,
            'contentId': content_id,
            'questionId': questions[1].id,
            'answer': '3818 Grindelwald'
        }))

        rp = ReviewPipeline(self.task_id, 2, self.userId)
        review_task_id = rp.create_review_task()

        #print('review_task_id'+ str(review_task_id))

        review_contents = Content.select().where(Content.task == review_task_id)
        review_question_id = Question.get(Question.task == review_task_id).id

        for content in review_contents:
            r = requests.post(base_api_url + '/worker/' + str(other_user_id) + '/answers', data=json.dumps({
                'userId': other_user_id,
                'contentId': content.id,
                'questionId': review_question_id,
                'answer': 'Yes'
            }))

        result = rp.get_answers()

        print('\nmake_review_pipeline: ' + json.dumps(result))