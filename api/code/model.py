from peewee import *

from api.code.database import mysql_db


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


class Content(BaseModel):
    contentId = PrimaryKeyField()
    dataJSON = TextField()
    taskId = ForeignKeyField(Task)


class Answer(BaseModel):
    dataRowAnswerId = PrimaryKeyField()
    answer = TextField()
    userId = ForeignKeyField(User)
    contentId = ForeignKeyField(Content)
    questionId = ForeignKeyField(Question)
