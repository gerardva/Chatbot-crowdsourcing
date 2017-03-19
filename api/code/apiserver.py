import json

from peewee import *
# from database import db

# from apifuncs.worker.GetRandomTask import GetRandomTaskResource
# from apifuncs.worker.SubmitAnswer import SubmitAnswerResource
# from apifuncs.worker.ListTasks import ListTasksResource
# from apifuncs.worker.CreateNewUser import CreateNewUserResource
# from apifuncs.requester.InputTask import InputTaskResource
# from apifuncs.requester.GetTaskResults import GetTaskResultsResource
from api.code.apifuncs.api import QuoteResource
from api.code.settings import settings
from playhouse.shortcuts import model_to_dict

mysqlSettings = settings["mysql"]

mysql_db = MySQLDatabase(host=mysqlSettings["host"],
                         user=mysqlSettings["user"],
                         passwd=mysqlSettings["passwd"],
                         database=mysqlSettings["db"])


def add_api_routes(app):
    app.add_route('/quote', QuoteResource())
    app.add_route('/worker/getRandomJob', GetRandomJobResource())
    app.add_route('/worker/submitAnswer', SubmitAnswerResource())
    app.add_route('/worker/listTasks', ListTasksResource())
    app.add_route('/worker/createNewUser', CreateNewUserResource())
    app.add_route('/requester/inputTask', InputTaskResource())
    app.add_route('/requester/getTaskResults', GetTaskResultsResource())


class BaseModel(Model):
    class Meta:
        database = mysql_db


class User(BaseModel):
    userId = PrimaryKeyField()
    score = FloatField(default=0.0)


class Task(BaseModel):
    taskId = PrimaryKeyField()
    userId = ForeignKeyField(User, related_name="tasks_created")


class Question(BaseModel):
    questionId = PrimaryKeyField()
    key = CharField()
    question = TextField()
    taskId = ForeignKeyField(Task)


class DataRow(BaseModel):
    dataRowId = PrimaryKeyField()
    dataJSON = TextField()
    taskId = ForeignKeyField(Task)


class DataRowAnswer(BaseModel):
    dataRowAnswerId = PrimaryKeyField()
    answer = TextField()
    userId = ForeignKeyField(User)
    dataRowId = ForeignKeyField(DataRow, related_name="answers")


mysql_db.create_tables([User, Task, Question, DataRow, DataRowAnswer], safe=True)


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

        answer = DataRowAnswer.create(answer=req_as_json['answer'],
                                      userId=req_as_json['userId'],
                                      dataRowId=req_as_json['dataRowId'])

        answer.save()

        resp.body = json.dumps({
            'success': True,
            'reward': 100000000000
        })


class GetRandomJobResource:
    def on_get(self, req, resp):
        dataRow = DataRow.select().order_by(fn.Rand()).first()

        questions = Question.select().join(Task).where(Task.taskId == dataRow.taskId).get()

        resp.body = json.dumps({
            'dataRow': json.dumps(model_to_dict(dataRow)),
            'questions': json.dumps(model_to_dict(questions))
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

        for dataRow in task_as_json['dataRows']:
            DataRow.create(dataJSON=dataRow, taskId=task.taskId)

        resp.body = json.dumps({'taskId': task.taskId})


class GetTaskResultsResource:
    def on_post(self, req, resp):
        req_as_json = json.loads(req.stream.read().decode('utf-8'))

        results = DataRowAnswer.select().join(DataRow).where(DataRow.taskId == req_as_json['taskId'])

        resp.body = json.dumps({
            'results': json.load(results)
        })