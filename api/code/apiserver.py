import json

from api.code.apifuncs.api import QuoteResource
from api.code.model import *


def add_api_routes(app):
    app.add_route('/quote', QuoteResource())
    app.add_route('/worker/tasks', WorkerTasksResource())
    app.add_route('/worker/answers', WorkerAnswersResource())
    app.add_route('/worker/users', WorkerUsersResource())
    app.add_route('/requester/tasks', RequesterTasksResource())
    app.add_route('/requester/tasks/{task_id}/answers', RequesterTasksAnswersResource())


mysql_db.create_tables([User, Task, Question, Content, Answer], safe=True)


class WorkerAnswersResource:
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


class WorkerTasksResource:
    def on_get(self, req, resp):
        # read parameters
        limit = req.get_param("limit")
        order = req.get_param("order")
        # start building query
        contents = Content.select()
        if order == "random":
            contents.order_by(fn.Rand())
        if limit:
            try:
                limit_int = int(limit)
                contents = contents.limit(limit_int)
            except ValueError:
                # ignore limit parameter if it is not an integer
                pass

        tasks = []
        # TODO: query by task, so user can get a list of different tasks to choose from instead of different contents
        for contents in contents:
            questions = Question.select().join(Task).where(Task.id == contents.taskId)

            # TODO: order questions by key
            questions_json = []
            for question in questions:
                questions_json.append({
                    'questionId': question.id,
                    'key': question.key,
                    'question': question.question,
                })

            # TODO: put this in a single join at the start, to prevent generating multiple queries
            task = contents.taskId

            tasks.append({
                'taskId': task.id,
                'contentId': contents.id,
                'content': contents.dataJSON,
                'questions': questions_json
            })
        resp.body = json.dumps(tasks)


class WorkerUsersResource:
    def on_get(self, req, resp):
        user = User.create()
        resp.body = json.dumps({'userId': user.id})


class RequesterTasksResource:
    def on_post(self, req, resp):
        print("task post called!")
        task_as_json = json.loads(req.stream.read().decode('utf-8'))
        task = Task.create(userId=task_as_json['userId'])
        task.save()

        for questionKey in task_as_json['questionRows'].keys():
            question_string = task_as_json['questionRows'][questionKey]
            new_question = Question.create(key=questionKey, question=question_string, taskId=task.id)
            new_question.save()

        Content.create(dataJSON=task_as_json['data'], taskId=task.id)

        resp.body = json.dumps({'taskId': task.id})


class RequesterTasksAnswersResource:
    def on_get(self, req, resp, task_id):
        try:
            task_id_int = int(task_id)

            # todo: get all answers grouped by content they relate to
            print(task_id_int)
            answers = Answer.select(Answer, Content, Task).join(Content).join(Task).where(Task.id == task_id_int)

            answers_list = []
            for answer in answers:
                answers_list.append({
                    'answer': answer.answer,
                    'contentId': answer.contentId.id,
                    'taskId': answer.contentId.taskId.id
                })
            resp.body = json.dumps(answers_list)
        except ValueError:
            pass
