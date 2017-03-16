#!/usr/bin/python

import json
import os
from urllib.parse import urlparse

with open('config/settings.json') as settings_file:
    settings = json.load(settings_file)
    # overwrite database config with database url if its environment variable is set
    if 'CLEARDB_DATABASE_URL' in os.environ:
        db_url = urlparse(os.environ['CLEARDB_DATABASE_URL'])
        settings['mysql'].update({
            "host": db_url.hostname,
            "user": db_url.username,
            "passwd": db_url.password,
            "db": db_url.path[1:]
        })