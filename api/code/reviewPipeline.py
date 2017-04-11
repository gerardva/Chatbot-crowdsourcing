from itertools import groupby
from api.code.model import *

import requests
import json
import re

#TODO this should be imported form settings
WAITRESS_PORT = 5000
base_api_url = 'http://localhost:'+str(WAITRESS_PORT)

class ReviewPipeline:
    def __init__(self, task_id, amount_of_reviews, requester_user_id, review_task_id=None):
        self.task_id = task_id
        self.amount_of_reviews = amount_of_reviews
        self.user_id = requester_user_id
        self.review_task_id = review_task_id


    def create_review_task(self):
        r = requests.get(base_api_url+'/requester/tasks/'+ str(self.task_id) + '/answers?elaborate=true')
        r_as_json = r.json()

        print(r.text)
        print(json.dumps(r_as_json[0]))

        # todo implement exclude userids, so a review cant be done by the person who answered the question
        review_task = {
            'userId': self.user_id,
            'description': self.review_task_description_maker(),
            'canNotMake': [],
            'content': [],
            'questionRows': []
        }

        for elaborate_answer in r_as_json:
            review_task['questionRows'].append(self.review_question_maker(elaborate_answer))
            for i in range(self.amount_of_reviews):
                review_task['canNotMake'].append(self.review_can_not_answer_maker(elaborate_answer))
                review_task['content'].append(self.review_content_description_maker(elaborate_answer))

        print('\n')
        print(json.dumps(review_task))

        r = requests.post(base_api_url+'/requester/tasks', data=json.dumps(review_task))
        print(r.text)
        r_as_json = json.loads(r.text)
        self.review_task_id = r_as_json['taskId']
        return r_as_json['taskId']

    def review_task_description_maker(self):
        base_desc = 'Review of the following task: '
        r = requests.get(base_api_url+'/requester/tasks?taskId='+str(self.task_id))
        r_as_json = r.json()
        base_desc += r_as_json['description']
        return base_desc

    def review_can_not_answer_maker(self, elaborate_answer):
        return [elaborate_answer['userId']]

    def review_content_description_maker(self, elaborate_answer):
        content = elaborate_answer['content']['dataJSON']

        content['reviewQuestion'] = elaborate_answer['question']['question']
        content['reviewAnswer'] = elaborate_answer['answer']

        print(content)
        return content

    def review_question_maker(self, elaborate_answer):
        original_answer = elaborate_answer['answer']
        original_question = elaborate_answer['question']['question']

        review_question = {
            'question': 'Is "{answer}" a good answer for the question: "{question}"?',
            'answerSpecification': {
                'type': 'option',
                'options': ['Yes', 'No']
            }
        }

        return review_question

    def get_answers(self):
        r = requests.get(base_api_url + '/requester/tasks/' + str(self.review_task_id) + '/answers')

        print('get_ansers: '+r.text)
        r_as_json = json.loads(r.text)

        grouped_answers = {}
        for k, g in groupby(r_as_json, key=lambda x: x['questionId']):
            grouped_answers[k] = list(g)

        print(json.dumps(grouped_answers))

        for key, answer_group in grouped_answers.items():
            print(json.dumps(answer_group))
            yes_count = 0
            for answer in answer_group:
                if answer['answer'] == 'Yes':
                    yes_count += 1
            if yes_count < self.amount_of_reviews:
                grouped_answers.remove(answer_group)

        result = []
        for key, answer_group in grouped_answers.items():
            question_id = answer_group[0]['questionId']
            content_id = answer_group[0]['contentId']
            # todo make question fetchable, so model can be removed from this code
            # then the api and pipeline are fully seperate again
            review_question = Question.get(Question.id == question_id)

            print(review_question.as_json())
            # todo allow a way of storing the original question and answer without this ugly thing.
            # maybe a private data area within the content?
            res = re.search('\"(.*)\".*\"(.*)\"', review_question.question)
            answer = res.group(1)
            question = res.group(2)
            result.append({
                'questionId': question_id,
                'contentId': content_id,
                'question': question,
                'answer': answer
            })

        return result
