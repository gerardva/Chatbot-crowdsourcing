import json
import requests
import chatbot.facebook as Facebook
from chatbot.logger import log

api_url = "https://fathomless-cove-38602.herokuapp.com"  # no trailing slash
api_methods = {
    'GET': requests.get,
    'POST': requests.post,
    'PUT': requests.put
}

def send_message(recipient_id, message_text, quick_replies=None):
    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text,
            "quick_replies": quick_replies
        }
    })

    res = Facebook.facebook_send(data)
    return res

def send_image(recipient_id, image_url):
    log("sending image to {recipient}: {image}".format(recipient=recipient_id, image=image_url))

    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "attachment": {
                "type": "image",
                "payload": {
                    "url": image_url
                }
            }
        }
    })

    res = Facebook.facebook_send(data)
    return res

def call_api(method, url, data=None):
    r_method = api_methods.get(method.upper())
    if r_method is None:
        log("Unknown method {method} for API call".format(method=method))
        return False

    call_url = api_url + url
    r = r_method(call_url, json=data)

    if r.status_code != 200:
        log("{status_code} encountered when calling {url}".format(status_code=r.status_code, url=call_url))
        log(r.text)
        return False

    return r.json()

def get_random_task():
    res = call_api("GET", "/worker/tasks?order=random&limit=1")

    if not res:
        return False

    task = res[0]  # Pick the only question in the list
    return task

def post_answer(answer, user_id, question_id, content_id):
    data = {
        "answer": answer,
        "userId": user_id,
        "questionId": question_id,
        "contentId": content_id  # TODO: Why is contentId needed?
    }

    res = call_api("POST", "/worker/answers", data)
    if not res:
        return False

    return True
