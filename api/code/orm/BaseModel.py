#!/usr/bin/python

import peewee
from peewee import *

class BaseModel(Model):
    class Meta:
        database = db