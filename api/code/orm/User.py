#!/usr/bin/python

import peewee
from peewee import *
from BaseModel import BaseModel

class User(BaseModel):
    userId = PrimaryKeyField()
    score = FloatField()