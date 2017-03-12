import falcon
import json
from waitress import serve
from peewee import *
# from database import db
from apifuncs.api import QuoteResource
# from apifuncs.worker.GetRandomTask import GetRandomTaskResource
# from apifuncs.worker.SubmitAnswer import SubmitAnswerResource
# from apifuncs.worker.ListTasks import ListTasksResource
# from apifuncs.worker.CreateNewUser import CreateNewUserResource
# from apifuncs.requester.InputTask import InputTaskResource
# from apifuncs.requester.GetTaskResults import GetTaskResultsResource

from settings import settings

mysqlSettings = settings["mysql"]

mysql_db = MySQLDatabase('ir', host=mysqlSettings["host"], 
                               user=mysqlSettings["user"],
                               passwd=mysqlSettings["passwd"])


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


mysql_db.create_tables([DataRow, DataRowAnswer, Question, Task, User], safe=True)


class PeeweeConnectionMiddleware(object):
    def process_request(self, req, resp):
        mysql_db.connect()

    def process_response(self, req, resp, resource):
        if not mysql_db.is_closed():
            mysql_db.close()

api = falcon.API(middleware=[PeeweeConnectionMiddleware()])


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
        req_as_json = json.loads(req.stream.read())

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
        dataRow = DataRow.select().order_by(fn.Rand()).limit(1)

        questions = Question.select().join(Task).where(Task.taskId == dataRow.taskId)

        resp.body = json.dumps({
            'dataRow': json.load(dataRow),
            'questions': json.load(questions)
        })


class CreateNewUserResource:
    def on_get(self, req, resp):
        u = User.create()
        resp.body = json.dumps({'userId': u.userId})


class InputTaskResource:
    def on_post(self, req, resp):
        task_as_json = json.loads(req.stream.read())
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
        req_as_json = json.loads(req.stream.read())

        results = DataRowAnswer.select().join(DataRow).where(DataRow.taskId == req_as_json['taskId'])

        resp.body = json.dumps({
            'results': json.load(results)
        })


api.add_route('/quote', QuoteResource())
api.add_route('/worker/getRandomJob', GetRandomJobResource())
api.add_route('/worker/submitAnswer', SubmitAnswerResource())
api.add_route('/worker/listTasks', ListTasksResource())
api.add_route('/worker/createNewUser', CreateNewUserResource())
api.add_route('/requester/inputTask', InputTaskResource())
api.add_route('/requester/getTaskResults', GetTaskResultsResource())


serve(api)
