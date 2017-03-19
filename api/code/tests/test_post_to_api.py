#!/bin/usr/python

import requests
import json

r = requests.get('http://localhost:5000/worker/createNewUser')

print(r.text)

r = requests.post('http://localhost:5000/requester/inputTask', data=json.dumps({
    'userId': 2,
    'dataRows': [
        {'pictureUrl': 'someUrl'}
    ],
    'questionRows': {
        'q1': 'what location',
        'q2': 'other q'
    }
}))

# print(r.text)

r = requests.post('http://localhost:5000/worker/submitAnswer', data=json.dumps({
    'userId': 2,
    'dataRowId': 2,
    'answer': 'this is truly a legit answer'
}))

print(r.text)
