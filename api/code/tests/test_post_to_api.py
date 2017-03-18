#!/bin/usr/python

import requests
import json

r = requests.get('http://localhost:8080/worker/createNewUser')

print(r.text)

# r = requests.post('http://localhost:8080/requester/inputTask', data=json.dumps({
#     'userId': 1,
#     'dataRows': [
#         {'pictureUrl': 'someUrl'}
#     ],
#     'questionRows': {
#         'q1': 'what location',
#         'q2': 'other q'
#     }
# }))
#
# print(r.text)
#
# r = requests.post('http://localhost:8080/worker/submitAnswer', data=json.dumps({
#     'userId': 1,
#     'dataRowId': 1,
#     'answer': 'this is truly a legit answer'
# }))
#
# print(r.text)
