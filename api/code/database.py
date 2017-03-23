import json
import os
from urllib.parse import urlparse

from peewee import MySQLDatabase

with open('api/config/settings.json') as settings_file:
    mysql_settings = json.load(settings_file)['mysql']
    # overwrite database config with database url if its environment variable is set
    if 'CLEARDB_DATABASE_URL' in os.environ:
        db_url = urlparse(os.environ['CLEARDB_DATABASE_URL'])
        mysql_settings.update({
            "host": db_url.hostname,
            "user": db_url.username,
            "passwd": db_url.password,
            "db": db_url.path[1:]
        })

    mysql_db = MySQLDatabase(host=mysql_settings["host"],
                             user=mysql_settings["user"],
                             passwd=mysql_settings["passwd"],
                             database=mysql_settings["db"])