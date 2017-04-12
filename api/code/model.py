import json

from peewee import *

from api.code.database import mysql_db


class BaseModel(Model):
    class Meta:
        database = mysql_db


class User(BaseModel):
    id = PrimaryKeyField()
    score = DecimalField(default=0.0)
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
    user = ForeignKeyField(User, related_name="tasks_created")

    def as_json(self):
        return {
            'id': self.id,
            'description': self.description,
            'userId': self.user.id
        }


class Question(BaseModel):
    id = PrimaryKeyField()
    index = IntegerField()
    question = TextField()
    answerSpecificationJSON = TextField()
    task = ForeignKeyField(Task, related_name='questions')

    def as_json(self):
        return {
            'id': self.id,
            'index': self.index,
            'question': self.question,
            'answerSpecificationJSON': json.loads(self.answerSpecificationJSON),
            'taskId': self.task.id
        }


class Content(BaseModel):
    id = PrimaryKeyField()
    dataJSON = TextField(null=True)
    task = ForeignKeyField(Task)

    def as_json(self):
        return {
            'id': self.id,
            'dataJSON': json.loads(self.dataJSON),
            'taskId': self.task.id
        }


class Location(BaseModel):
    content = ForeignKeyField(Content, primary_key=True, related_name="location")
    longitude = FloatField()
    latitude = FloatField()


class Answer(BaseModel):
    answer = TextField()
    user = ForeignKeyField(User)
    content = ForeignKeyField(Content)
    question = ForeignKeyField(Question)

    def as_json(self):
        return {
            'id': self.id,
            'userId': self.user.id,
            'contentId': self.user.id,
            'questionId': self.question.id
        }

    class Meta:
        primary_key = CompositeKey('user', 'content', 'question')


class CanNotAnswer(BaseModel):
    user = ForeignKeyField(User)
    content = ForeignKeyField(Content)

    class Meta:
        primary_key = CompositeKey('user', 'content')
