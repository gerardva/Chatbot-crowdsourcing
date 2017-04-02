import json
import chatbot.api_helper as Api
import chatbot.facebook_helper as Facebook
from chatbot.logger import log

user_states = {}
greetings = {"hi", "hey", "hello", "greetings"}


def handle_message(messaging_event):
    message = construct_message(messaging_event)

    # If we haven't seen the user before, check if the user is registered
    if user_states.get(message["sender_id"]) is None:
        get_user(message["sender_id"])

    user_state = user_states[message["sender_id"]]  # This should not be None after get_user

    if user_state["state"] == "idle":
        handle_message_idle(message)

    elif user_state["state"] == "given_task":
        handle_message_given_task(message)

    # Handle default case
    else:
        Facebook.send_message(message["sender_id"], "I did not understand your message")


def handle_message_idle(message):
    # Handle giving task
    if message.get("coordinates") or message.get("quick_reply_payload") == "task" or message[
        "text"] == "Give me a task":
        task = Api.get_random_task()
        if not task:
            Facebook.send_message(message["sender_id"], "Sorry, something went wrong when retrieving your task")
            return

        questions = task["questions"]
        data_json = json.loads(task["content"])

        user_states[message["sender_id"]] = {
            "state": "given_task",
            "user_id": user_states[message["sender_id"]]["user_id"],
            "task_id": task["taskId"],
            "questions": questions,
            "current_question": 0,
            "content_id": task["contentId"]
        }
        log(user_states)

        Api.send_image(message["sender_id"], data_json["pictureUrl"])
        Facebook.send_message(message["sender_id"], questions[0]["question"])

    # Handle initial message
    else:  # str.lower(message["text"]) in greetings:
        quick_replies = [{
            "content_type": "location"
        }, {
            "content_type": "text",
            "title": "Give me a task",
            "payload": "task"
        }]

        Facebook.send_message(message["sender_id"], "What's up? I can give you a task, but if you send your location "
                                           "I can give you even cooler tasks.", quick_replies)

def handle_message_given_task(message):
    if message["text"] == "Give me a task":
        Facebook.send_message(message["sender_id"], "You already have a task")
        return

    user_state = user_states[message["sender_id"]]
    current_question = user_state["current_question"]
    questions = user_state["questions"]
    answer_type = questions[current_question]["answerType"]

    answer = None
    if answer_type == "plaintext":
        if not message["text"]:
            Facebook.send_message(message["sender_id"], "I was expecting text as an answer to this question..")
            return

        answer = message["text"]

    if answer_type == "image":
        if not message["image"]:
            Facebook.send_message(message["sender_id"], "I was expecting an image as an answer to this question..")
            return

        answer = message["image"]

    user_id = user_state["user_id"]
    question_id = questions[current_question]["questionId"]
    content_id = user_state["content_id"]

    res = Api.post_answer(answer, user_id, question_id, content_id)

    if not res:
        Facebook.send_message(message["sender_id"], "Sorry, something went wrong when submitting your answer")
        return

    if current_question == len(questions) - 1:
        Facebook.send_message(message["sender_id"], "Thank you for your answer, you're done!")
        user_states[message["sender_id"]] = {
            "state": "idle",
            "user_id": user_state["user_id"]
        }

        handle_message_idle(message)

    else:
        user_state["current_question"] = current_question + 1
        Facebook.send_message(message["sender_id"], "Thank you for your answer, here comes the next question!")
        Facebook.send_message(message["sender_id"], questions[current_question + 1]["question"])


def construct_message(messaging_event):
    message = {}

    message["sender_id"] = messaging_event["sender"]["id"]  # the facebook ID of the person sending you the message

    message["text"] = messaging_event["message"].get("text", "")

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


def get_user(sender_id):
    # TODO: Register user if not registered yet
    user = Api.call_api("GET", "/worker/users");
    if not user:
        return False

    if user_states.get(sender_id) is None:
        user_states[sender_id] = {
            "state": "idle",
            "user_id": user["userId"]
        }
