import requests
import json


def main():
    r = requests.post('http://localhost:5000/worker/', data=json.dumps({
        'facebookId': 'this is totally a legit facebook id'
    }))

    print('returned user json: ' + r.text)
    r_as_json = json.loads(r.text)
    user_id = r_as_json['userId']

    r = requests.post('http://localhost:5000/requester/tasks', data=json.dumps({
        "userId": user_id,
        "description": "Take a picture of a specific Albert Heijn shelf",
        "content": [
            {'location': {'longitude': 4.3731616,
                          'latitude': 51.9989083}}
        ],
        "questionRows": [
            {
                "question": "Please go to Albert Heijn Delft at Mercuriusweg 16 "
                            "and take a picture of the shelf containing eggs. "
                            "Make sure you take the picture from the front and include all eggs in the frame.",
                "answerSpecification": {"type": "image"}
            },
            {
                "question": "What is the name of the product in the bottom left of the shelf?",
                "answerSpecification": {"type": "plaintext"}
            },
            {
                "question": "What is the name of the product in the top right of the shelf?",
                "answerSpecification": {"type": "plaintext"}
            },
            {
                "question": "How many cartons of ‘AH Scharreleieren klasse M’ (6 pieces) are there on the shelf?",
                "answerSpecification": {"type": "plaintext"}
            }
        ]
    }))

    print(str(r.status_code))

if __name__ == '__main__':
    main()
