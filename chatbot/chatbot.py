import json
import os
import sys

import falcon
import requests


def add_chatbot_routes(app):
    app.add_route('/chatbot', ChatbotResource())


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

                        sender_id = messaging_event["sender"]["id"]  # the facebook ID of the person sending you the message
                        recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                        message_text = messaging_event["message"]["text"]  # the message's text

                        send_message(sender_id, "got it, thanks!")

                    if messaging_event.get("delivery"):  # delivery confirmation
                        pass

                    if messaging_event.get("optin"):  # optin confirmation
                        pass

                    if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                        pass

        resp.status = falcon.HTTP_200
        resp.content_type = "text/html"
        resp.body = "ok"


def send_message(recipient_id, message_text):
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
            "text": message_text
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


def log(message):  # simple wrapper for logging to stdout on heroku
    print(str(message))
    sys.stdout.flush()
