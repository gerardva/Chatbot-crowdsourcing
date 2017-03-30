from peewee import *

from api.code.database import mysql_db


class BaseModel(Model):
    class Meta:
        database = mysql_db


class User(BaseModel):
    id = PrimaryKeyField()
    score = FloatField(default=0.0)


class Task(BaseModel):
    id = PrimaryKeyField()
    description = TextField()
    userId = ForeignKeyField(User, related_name="tasks_created")


class Question(BaseModel):
    id = PrimaryKeyField()
    index = IntegerField()
    question = TextField()
    contentType = TextField()
    taskId = ForeignKeyField(Task)


class Content(BaseModel):
    id = PrimaryKeyField()
    dataJSON = TextField()
    taskId = ForeignKeyField(Task)

class Location(BaseModel):
    contentId = ForeignKeyField(Content, primary_key=True)
    longitude = FloatField()
    latitude = FloatField()

class Answer(BaseModel):
    answer = TextField()
    userId = ForeignKeyField(User)
    contentId = ForeignKeyField(Content)
    questionId = ForeignKeyField(Question)

    class Meta:
        primary_key = CompositeKey('userId', 'contentId', 'questionId')
