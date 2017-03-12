#!/usr/bin/python

import peewee
from peewee import *
from Task import Task
from BaseModel import BaseModel

class Question(BaseModel):
    questionId = PrimaryKeyField()
    key = characterField()
    question = textField()
    taskId = ForeignKeyField(Task)