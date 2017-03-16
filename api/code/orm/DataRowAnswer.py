#!/usr/bin/python

import peewee
from peewee import *
from User import User
from Question import Question
from BaseModel import BaseModel

class DataRowAnswer(BaseModel):
    dataRowAnswerId = PrimaryKeyField()
    answer = TextField()
    userId = ForeignKeyField(User)
    questionId = ForeignKeyField(Question, related_name="answers")