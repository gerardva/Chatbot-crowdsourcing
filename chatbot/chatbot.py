import json
import os
import sys

import falcon
import requests


def add_chatbot_routes(app):
    app.add_route('/chatbot', ChatbotResource())

api_url = "https://fathomless-cove-38602.herokuapp.com" # no trailing slash
user_states = {}
greetings = {"hi", "hey", "hello", "greetings"}

class ChatbotResource:
    def on_get(self, req, resp):
        # when the endpoint is registered as a webhook, it must echo back
        # the 'hub.challenge' value it receives in the query arguments
        resp.content_type = "text/html"
        if req.get_param("hub.mode") == "subscribe" and req.get_param("hub.challenge"):
            if req.get_param("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
                resp.body = req.get_param("hub.challenge")
            else:
                resp.status = falcon.HTTP_403
                resp.body = "Verification token mismatch"
        else:
            resp.body = "Hello World"

    def on_post(self, req, resp):
        # endpoint for processing incoming messaging events

        data = json.loads(req.stream.read().decode('utf-8'))
        log(data)  # you may not want to log every incoming message in production, but it's good for testing

        if data["object"] == "page":

            for entry in data["entry"]:
                for messaging_event in entry["messaging"]:

                    if messaging_event.get("message"):  # someone sent us a message
                        handle_message(messaging_event)

                    if messaging_event.get("delivery"):  # delivery confirmation
                        pass

                    if messaging_event.get("optin"):  # optin confirmation
                        pass

                    if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                        pass

        resp.status = falcon.HTTP_200
        resp.content_type = "text/html"
        resp.body = "ok"


def handle_message(messaging_event):
    sender_id = messaging_event["sender"]["id"]  # the facebook ID of the person sending you the message
    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID

    message_text = messaging_event["message"].get("text", "")  # the message's text

    if user_states.get(sender_id) is None:
        user_states[sender_id] = {
            "state" : "idle"
        }

    quick_reply = messaging_event["message"].get("quick_reply")
    quick_reply_payload = quick_reply["payload"] if quick_reply else None

    attachments = messaging_event["message"].get("attachments")
    coordinates = None
    if attachments is not None:
        attachment = attachments[0]
        attachment_type =  attachment["type"]
        if attachment_type == "location":
            coordinates = attachment["payload"]["coordinates"]
        if attachment_type == "image":
            pass # TODO: handle image


    #if not message_text:
    #    send_message(sender_id, "Error, self-destructing in 5 seconds")
    #    return

    if str.lower(message_text) in greetings and user_states[sender_id]["state"] == "idle":
        quick_replies = [{
            "content_type": "location"
          }, {
            "content_type": "text",
            "title": "Give me a task",
            "payload": "task"
          }
        ]
        send_message(sender_id, "What's next? Send your location to get even cooler tasks.", quick_replies)

    elif message_text == "Give me a task" and user_states[sender_id]["state"] == "given_task":
        send_message(sender_id, "You already have a task")

    elif (coordinates or quick_reply_payload == "task" or message_text == "Give me a task") and user_states[sender_id]["state"] == "idle":
        r = requests.get("{base_url}/worker/getRandomJob".format(base_url=api_url))
        if r.status_code != 200:
            log(r.status_code)
            log(r.text)

        task = r.json()
        question = task["questions"][0]  # TODO: Pick question intelligently
        data_json = json.loads(task["content"])[0]  # TODO: When do we have multiple content?

        user_states[sender_id] = {
            "state": "given_task",
            "task_id": task["taskId"],
            "question_id": question["questionId"],
            "content_id": task["contentId"]
        }
        log(user_states)

        send_image(sender_id, data_json["pictureUrl"])
        send_message(sender_id, question["question"])

    elif message_text.startswith("Answer: "):
        if user_states[sender_id] is None or user_states[sender_id]["state"] != "given_task":
            send_message(sender_id, "You do not have a task assigned")
            return

        task = user_states[sender_id]["task_id"]
        question_id = user_states[sender_id]["question_id"]
        content_id = user_states[sender_id]["content_id"]

        data = {
            "answer": message_text[8:],
            "userId": 2,  # TODO: Fix registration
            "questionId": user_states[sender_id]["question_id"],
            "contentId": user_states[sender_id]["content_id"]  # TODO: Why is contentId needed?
        }
        r = requests.post("{base_url}/worker/submitAnswer".format(base_url=api_url),
                          json=data)

        if r.status_code != 200:
            log(r.status_code)
            log(r.text)

        user_states[sender_id] = None

        send_message(sender_id, "Thank you for your answer!")
        user_states[sender_id] = {
            "state": "idle"
        }

        # TODO: This is duplicate code, should be refactored
        quick_replies = [{
            "content_type": "location"
        }, {
            "content_type": "text",
            "title": "Give me a task",
            "payload": "task"
        }
        ]
        send_message(sender_id, "What's next? Send your location to get even cooler tasks.", quick_replies)

    else:
        send_message(sender_id, "I did not understand your message")


def send_message(recipient_id, message_text, quick_replies=None):
    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))
    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text,
            "quick_replies": quick_replies
        }
    })
    log("Sending data: {data}".format(data=data))
    r = requests.post("https://graph.facebook.com/v2.8/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


# TODO: This is duplicate code
def send_image(recipient_id, image_url):
    log("sending image to {recipient}: {text}".format(recipient=recipient_id, text=image_url))

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
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

    r = requests.post("https://graph.facebook.com/v2.8/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


def log(message):  # simple wrapper for logging to stdout on heroku
    print(str(message))
    sys.stdout.flush()
