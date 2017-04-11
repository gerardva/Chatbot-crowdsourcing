import json

from peewee import *

from api.code.database import mysql_db


class BaseModel(Model):
    class Meta:
        database = mysql_db


class User(BaseModel):
    id = PrimaryKeyField()
    score = FloatField(default=0.0)
    facebookId = TextField()

    def as_json(self):
        return {
            'id': self.id,
            'score': self.score,
            'facebookId': self.facebookId
        }


class Task(BaseModel):
    id = PrimaryKeyField()
    description = TextField()
    userId = ForeignKeyField(User, related_name="tasks_created")

    def as_json(self):
        return {
            'id': self.id,
            'description': self.description,
            'userId': self.userId.id
        }


class Question(BaseModel):
    id = PrimaryKeyField()
    index = IntegerField()
    question = TextField()
    answerSpecificationJSON = TextField()
    taskId = ForeignKeyField(Task, related_name='questions')

    def as_json(self):
        return {
            'id': self.id,
            'index': self.index,
            'question': self.question,
            'answerSpecificationJSON': json.loads(self.answerSpecificationJSON),
            'taskId': self.taskId.id
        }


class Content(BaseModel):
    id = PrimaryKeyField()
    dataJSON = TextField(null=True)
    taskId = ForeignKeyField(Task)

    def as_json(self):
        return {
            'id': self.id,
            'dataJSON': json.loads(self.dataJSON),
            'taskId': self.taskId.id
        }


class Location(BaseModel):
    contentId = ForeignKeyField(Content, primary_key=True, related_name="location")
    longitude = FloatField()
    latitude = FloatField()


class Answer(BaseModel):
    answer = TextField()
    userId = ForeignKeyField(User)
    contentId = ForeignKeyField(Content)
    questionId = ForeignKeyField(Question)

    def as_json(self):
        return {
            'id': self.id,
            'userId': self.userId.id,
            'contentId': self.userId.id,
            'questionId': self.questionId.id
        }

    class Meta:
        primary_key = CompositeKey('userId', 'contentId', 'questionId')


class CanNotAnswer(BaseModel):
    userId = ForeignKeyField(User)
    contentId = ForeignKeyField(Content)

    class Meta:
        primary_key = CompositeKey('userId', 'contentId')
