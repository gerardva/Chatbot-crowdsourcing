import requests
import json

r = requests.get('http://localhost:5000/worker/createNewUser')

print(r.text)
r_as_json = json.loads(r.text)
userId = r_as_json['userId']

r = requests.post('http://localhost:5000/requester/inputTask', data=json.dumps({
    'userId': 2,
    'data': [
        {'pictureUrl': 'someUrl'}
    ],
    'questionRows': {
        'q1': 'what location',
        'q2': 'other q'
    }
}))

print(r.text)

r = requests.get('http://localhost:5000/worker/getRandomJob')

print(r.text)
r_as_json = json.loads(r.text)
contentId = r_as_json['contentId']
questionId = r_as_json['questions'][0]['questionId']


r = requests.post('http://localhost:5000/worker/submitAnswer', data=json.dumps({
    'userId': userId,
    'contentId': contentId,
    'questionId': questionId,
    'answer': 'this is truly a legit answer'
}))

print(r.text)
