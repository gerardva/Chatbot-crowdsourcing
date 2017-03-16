#!/usr/bin/python

import peewee
from peewee import *
from User import User
from BaseModel import BaseModel


class Task(BaseModel):
    taskId = PrimaryKeyField()
    userId = ForeignKeyField(User, related_name="tasks_created")    