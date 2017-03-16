#!/usr/bin/python

import json

with open('config/settings.json') as settings_file:
	settings = json.load(settings_file)
