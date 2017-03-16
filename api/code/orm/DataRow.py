#!/usr/bin/python

import peewee
from peewee import *
from Question import Question
from BaseModel import BaseModel

class DataRow(BaseModel):
    dataRowId = PrimaryKeyField()
    dataJSON = TextField()
    questionId = ForeignKeyField(Question)