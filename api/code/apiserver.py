import json

from api.code.apifuncs.api import QuoteResource
from api.code.model import *


def add_api_routes(app):
    app.add_route('/quote', QuoteResource())
    app.add_route('/worker/getRandomJob', GetRandomJobResource())
    app.add_route('/worker/submitAnswer', SubmitAnswerResource())
    app.add_route('/worker/listTasks', ListTasksResource())
    app.add_route('/worker/createNewUser', CreateNewUserResource())
    app.add_route('/requester/inputTask', InputTaskResource())
    app.add_route('/requester/getTaskResults', GetTaskResultsResource())


mysql_db.create_tables([User, Task, Question, Content, Answer], safe=True)


class ListTasksResource:
    def on_get(self, req, resp):
        """Handles GET requests"""

        result = {
            'tasks': []
        }

        for task in Task.select():
            result['tasks'].append(task.taskId)

        resp.body = json.dumps(result)


class SubmitAnswerResource:
    def on_post(self, req, resp):
        req_as_json = json.loads(req.stream.read().decode('utf-8'))

        answer = Answer.create(answer=req_as_json['answer'],
                               userId=req_as_json['userId'],
                               contentId=req_as_json['contentId'],
                               questionId=req_as_json['questionId'])

        answer.save()

        resp.body = json.dumps({
            'success': True,
            'reward': 100000000000
        })


class GetRandomJobResource:
    def on_get(self, req, resp):
        content = Content.select().order_by(fn.Rand()).first()

        questions = Question.select().join(Task).where(Task.taskId == content.taskId)

        questions_json = []
        for question in questions:
            questions_json.append({
                'questionId': question.questionId,
                'key': question.key,
                'question': question.question,
            })

        task = content.taskId

        resp.body = json.dumps({
            'taskId': task.taskId,
            'contentId': content.contentId,
            'content': content.dataJSON,
            'questions': questions_json
        })


class CreateNewUserResource:
    def on_get(self, req, resp):
        u = User.create()
        resp.body = json.dumps({'userId': u.userId})


class InputTaskResource:
    def on_post(self, req, resp):
        task_as_json = json.loads(req.stream.read().decode('utf-8'))
        task = Task.create(userId=task_as_json['userId'])
        task.save()

        for questionKey in task_as_json['questionRows'].keys():
            question_string = task_as_json['questionRows'][questionKey]
            new_question = Question.create(key=questionKey, question=question_string, taskId=task.taskId)
            new_question.save()

        Content.create(dataJSON=task_as_json['data'], taskId=task.taskId)

        resp.body = json.dumps({'taskId': task.taskId})


class GetTaskResultsResource:
    def on_post(self, req, resp):
        req_as_json = json.loads(req.stream.read().decode('utf-8'))

        results = Answer.select().join(Content).where(Content.taskId == req_as_json['taskId'])

        resp.body = json.dumps({
            'results': json.load(results)
        })
