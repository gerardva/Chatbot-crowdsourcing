import requests
import json
import time

HOST = 'localhost'
PORT = '5000'
user = ''



def main(user=None):
    message = raw_input("What's the message? ")
    if user == None:
        user = users(str.lower(raw_input("Who are you? (enter first letter of your name) ")))
    timestamp = int(time.time())


    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({  "object": "page",
  "entry": [
    {
      "messaging": [
        {
          "sender": {
            "id": user
          },
          "message": {
            "seq": 7425,
            "mid": "mid.$cAAaRu-bCUn5hCLcJoFa13HGOx2wQ",
            "text": str(message)
          },
          "timestamp": timestamp,
          "recipient": {
            "id": "1849085282000551"
          }
        }
      ],
      "id": "1849085282000551",
      "time": timestamp
    }
  ]
})
    print "Sending message..."
    r = requests.post("http://" + HOST + ":" + PORT + "/chatbot", headers=headers, data=data)
    print "Status: " + str(r.status_code)
    print "Response: " + r.text

    cont = raw_input("Send another message? (y/n) ")
    if cont == "y":
        main(user)


def users(letter):
    return {
        'g': "1106829549426992",
        'r': "1106829549426992",
        'k': "1106829549426992",
        'c': "1106829549426992",
        'n': "1106829549426992"
    }[letter]

if __name__ == '__main__':
    main()