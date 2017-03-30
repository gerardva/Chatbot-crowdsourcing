import requests
import json
import time

HOST = 'localhost'
PORT = '5000'
headers = {
    "Content-Type": "application/json"
}


def main(user=None):
    if user == None:
        user = users(str.lower(input("Who are you? (enter first letter of your name) ")))

    mode = input("What's your message? You can also send (L)ocation or (I)mage ")
    if mode.lower() == "l":
        send_location(user)
    elif mode.lower() == "i":
        send_image(user)
    else:
        send_message(mode, user)

    main(user)


def send_image(user):
    timestamp = int(time.time())
    data = json.dumps(
        {"object": "page",
           "entry": [
               {
                   "messaging": [
                       {
                           "sender": {
                               "id": user
                           },
                           'timestamp': timestamp,
                           "message": {
                               "seq": 7425,
                               "mid": "mid.$cAAaRu-bCUn5hCLcJoFa13HGOx2wQ",
                               'attachments': [
                                  {
                                    'type': 'image',
                                    'payload': {
                                      'url': 'https://scontent.xx.fbcdn.net/v/t34.0-12/17474547_10155045501141897_575052067_n.jpg?_nc_ad=z-m&oh=f189997052e850e8f9888f7c36ebc91e&oe=58D51524'
                                    }
                                  }
                               ]
                           }
                       }
                   ]
               }
           ]
         })
    post(data)


def send_location(user):
    timestamp = int(time.time())
    data = json.dumps(
        {"object": "page",
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
                               'attachments': [
                                  {
                                    'title': "The location",
                                    'url': 'https://l.facebook.com/l.php?u=https%3A%2F%2Fwww.bing.com%2Fmaps%2Fdefault.aspx%3Fv%3D2%26pc%3DFACEBK%26mid%3D8100%26where1%3D51.9989083%252C%2B4.3731616%26FORM%3DFBKPL1%26mkt%3Den-US&h=ATNs9YZt4bdKf0SRcLufuodHPWPmsiyZc4S0sSCy6joXcVAt6fFvzULh2X_iz4QcgiRN6mweeOZuv68NqQJm9qefkWIGMk_5S-xsItUsFraz&s=1&enc=AZMLPO7LzETfqwP58GKmd65wuybadqDlDXVNysaKYFhv5aT_AqhA356LB-lJMQGfU383wDZhGohJe3rBjkKhmp7k',
                                    'type': 'location',
                                    'payload': {
                                      'coordinates': {
                                        'lat': 51.9989083,
                                        'long': 4.3731616
                                      }
                                    }
                                  }
                                ]
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
    post(data)


def send_message(message, user):
    timestamp = int(time.time())
    data = json.dumps(
        {"object": "page",
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
    post(data)


def post(data):
    print("Sending message...")
    r = requests.post("http://" + HOST + ":" + PORT + "/chatbot", headers=headers, data=data)
    print("Status: " + str(r.status_code))
    print("Response: " + r.text)


def users(letter):
    return {
        'g': "1106829549426992",
        'r': "901711436598532",
        'k': "1838194942873561",
        'c': "1643601112334196"
    }[letter]

if __name__ == '__main__':
    main()