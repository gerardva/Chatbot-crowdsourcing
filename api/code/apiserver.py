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


mysql_db.create_tables([User, Task, Question, Content, Answer, Location], safe=True)


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
            contents = contents.order_by(fn.Rand())
        if limit:
            try:
                limit_int = int(limit)
                contents = contents.limit(limit_int)
            except ValueError:
                # ignore limit parameter if it is not an integer
                pass

        tasks = []
        # TODO: query by task, so user can get a list of different tasks to choose from instead of different contents
        for content in contents:
            questions = Question.select(Question, Task).join(Task).where(Task.id == content.taskId).order_by(Question.index)

            questions_json = []
            for question in questions:
                questions_json.append({
                    'questionId': question.id,
                    'index': question.index,
                    'question': question.question,
                    'answerType': question.answerType
                })

            task = content.taskId

            tasks.append({
                'taskId': task.id,
                'description': task.description,
                'contentId': content.id,
                'content': content.dataJSON,
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
        task = Task.create(userId=task_as_json['userId'],
                           description=task_as_json['description'])
        task.save()

        for index, question_json in enumerate(task_as_json['questionRows']):
            question_string = question_json['question']
            answer_type = question_json['answerType']
            new_question = Question.create(index=index,
                                           question=question_string,
                                           answerType=answer_type,
                                           taskId=task.id)
            new_question.save()

        for i, content in enumerate(task_as_json['data']):
            content_id = Content.create(dataJSON=json.dumps(task_as_json['data'][i]), taskId=task.id)

        if 'dataLocation' in task_as_json:
            add_location(content_id, task_as_json['dataLocation'])

        resp.body = json.dumps({'taskId': task.id})


def add_location(content_id, location_as_json):
    location = Location.create(contentId=content_id,
                               latitude=location_as_json['latitude'],
                               longitude=location_as_json['longitude'])
    location.save()


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
