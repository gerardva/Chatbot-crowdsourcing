import requests
import json

def main():
    r = requests.post('http://localhost:5000/worker/users', data=json.dumps({
        'facebookId': 'this is totally a legit facebook id'
    }))

    print('returned user json: ' + r.text)
    r_as_json = json.loads(r.text)
    userId = r_as_json['userId']


    r = requests.post('http://localhost:5000/requester/tasks', data=json.dumps({
        "userId": userId,
        "description": "Assess ground plan clarity",
        "content": [
            {"data": {"pictureUrl": "http://foodretaildesign.nl/wp-content/uploads/2016/11/plattegrond_AH_XL_Purmerend.jpg"}},
            {"data": {"pictureUrl": "http://www.ah-ouddorp.nl/website/wp-content/uploads/2014/07/Plattegrond-AH-Ouddorp.jpg"}},
            {"data": {"pictureUrl": "https://whmgipman.files.wordpress.com/2013/11/albert.jpg"}},
            {"data": {"pictureUrl": "http://www.ahsleeuwijk.nl/dev/wp-content/uploads/2015/01/plattegrond.jpg"}},
            {"data": {"pictureUrl": "https://myalbum.com/photo/pttj7Vvpc4Sd/1k0.jpg"}},
            {"data": {"pictureUrl": "http://www.politiekdelft.nl/mercuriusweg_016_delft_ah_plattegrond_001.jpg"}}
        ],
        "questionRows": [
            {
                "question": "From this ground plan, where do you think you can find the bananas? Enter the aisle number/description or 'I don't know' if you don't know.",
                "answerSpecification": {"type": "plaintext"}
			},
            {
                "question": "What about the eggs?",
                "answerSpecification": {"type": "plaintext"}
            },
            {
                "question": "And the spaghetti?",
                "answerSpecification": {"type": "plaintext"}
            },
            {
                "question": "Finally, where do you think you can find cola?",
                "answerSpecification": {"type": "plaintext"}
            },
            {
                "question": "Do you think this ground plan gave a clear overview of the store?",
                "answerSpecification": {"type": "option",
                             "options": ["Yes", "No"]}
            }
        ]
    }))


    print(str(r.status_code))

if __name__ == '__main__':
    main()