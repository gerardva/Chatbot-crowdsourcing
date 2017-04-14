import requests
import os
import json
from chatbot.logger import log


def construct_postback_message(messaging_event):
    message = {}

    message["sender_id"] = messaging_event["sender"]["id"]  # the facebook ID of the person sending you the message
    message["text"] = ""
    message["postback"] = messaging_event["postback"].get("payload", "")

    return message


def construct_message(messaging_event):
    message = {}

    message["sender_id"] = messaging_event["sender"]["id"]  # the facebook ID of the person sending you the message

    message["text"] = messaging_event.get("message").get("text", "")

    quick_reply = messaging_event["message"].get("quick_reply")
    message["quick_reply_payload"] = quick_reply["payload"] if quick_reply else None

    attachments = messaging_event["message"].get("attachments")
    if attachments is not None:
        attachment = attachments[0]  # Pick first attachment, discard the rest
        attachment_type = attachment["type"]
        if attachment_type == "location":
            message["coordinates"] = attachment["payload"]["coordinates"]
        if attachment_type == "image":
            message["image"] = attachment["payload"]["url"]

    return message


def construct_options_quick_replies(options):
    quick_replies = []
    for option in options:
        quick_reply = {
            "content_type": "text",
            "title": option,
            "payload": option
        }
        quick_replies.append(quick_reply)

    return quick_replies


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

    res = send(data)
    return res


def send_postback(recipient_id, message_text, button_title, payload):
    log("sending postback button to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "button",
                    "text": message_text,
                    "buttons": [
                        {
                            "type": "postback",
                            "title": button_title,
                            "payload": payload
                        }
                    ]
                }
            }
        }
    })

    res = send(data)
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

    res = send(data)
    return res


def send_list(recipient_id, elements):
    log("sending list of {num} elements to {recipient}".format(recipient=recipient_id, num=len(elements)))

    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "list",
                    "top_element_style": "compact",
                    "elements": elements
                }
            }
        }
    })

    res = send(data)
    return res


def send(data):
    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }

    log("Sending to Facebook: {data}".format(data=data))
    r = requests.post("https://graph.facebook.com/v2.8/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log("{status_code} encountered when sending Facebook data".format(status_code=r.status_code))
        log(r.text)
        return False

    return True


def get_user(facebook_id):
    fields = "first_name,last_name,profile_pic,locale,timezone,gender"
    access_token = os.environ["PAGE_ACCESS_TOKEN"]

    r = requests.get("https://graph.facebook.com/v2.8/{user_id}?fields={fields}&access_token={access_token}"
                     .format(user_id=facebook_id, fields=fields, access_token=access_token))

    if r.status_code != 200:
        log("{status_code} encountered when sending Facebook data".format(status_code=r.status_code))
        log(r.text)
        return False

    return r.json()
