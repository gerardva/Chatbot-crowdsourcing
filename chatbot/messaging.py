import json
import chatbot.api_helper as Api
import chatbot.facebook_helper as Facebook
from chatbot.logger import log

user_states = {}
greetings = {"hi", "hey", "hello", "greetings"}


def handle_postback_message(messaging_event):
    message = construct_postback_message(messaging_event)
    handle_message(message)

def handle_text_message(messaging_event):
    message = construct_message(messaging_event)
    handle_message(message)

def handle_message(message):

    # If we haven't seen the user before, check if the user is registered
    if user_states.get(message["sender_id"]) is None:
        get_user(message["sender_id"])

    user_state = user_states[message["sender_id"]]  # This should not be None after get_user

    if user_state["state"] == "idle":
        handle_message_idle(message)

    elif user_state["state"] == "given_task_options":
        handle_message_given_task_options(message)

    elif user_state["state"] == "given_task":
        handle_message_given_task(message)

    # Handle default case
    else:
        Facebook.send_message(message["sender_id"], "I did not understand your message")


def handle_message_idle(message):
    # Handle giving task
    if message.get("coordinates") or message.get("quick_reply_payload") == "random_task" or \
                    message["text"] == "Give me a random task":
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
        Facebook.send_postback(message["sender_id"], "To cancel this task, click the button. You can also cancel a task by typing 'Cancel'.", "Cancel task", "cancel_task")
        Facebook.send_image(message["sender_id"], data_json["pictureUrl"])
        Facebook.send_message(message["sender_id"], questions[0]["question"])

    # Handle giving multiple tasks
    elif message.get("quick_reply_payload") == "list_task" or message["text"] == "Give me a list of tasks to choose from":
        tasks = Api.get_tasks()
        if not tasks:
            Facebook.send_message(message["sender_id"], "Sorry, something went wrong when retrieving your task")
            return

        user_states[message["sender_id"]] = {
            "state": "given_task_options",
            "user_id": user_states[message["sender_id"]]["user_id"],
            "tasks": tasks
        }
        log(user_states)

        quick_replies = []
        mes = "I have " + str(len(tasks)) + " tasks for you: \n"
        for i, task in enumerate(tasks):
            mes += "Task " + str(i+1) + ": " + task["description"] + "\n"
            quick_replies.append({
                "content_type": "text",
                "title": "Task " + str(i+1),
                "payload": "task_" + str(i+1)
            })

        Facebook.send_message(message["sender_id"], mes, quick_replies)

    # Handle initial message
    else:  # str.lower(message["text"]) in greetings:
        quick_replies = [{
            "content_type": "location"
        }, {
            "content_type": "text",
            "title": "Give me a random task",
            "payload": "random_task"
        }, {
            "content_type": "text",
            "title": "Give me a list of tasks to choose from",
            "payload": "list_task"
        }]

        Facebook.send_message(message["sender_id"], "What's up? I can give you a task, but if you send your location "
                                                    "I can give you even cooler tasks.", quick_replies)


def handle_message_given_task_options(message):
    chosen_task_id = -1
    if message.get("quick_reply_payload"):
        try:
            chosen_task_id = int(message["quick_reply_payload"][5:])
        except:
            pass
    else:
        try:
            chosen_task_id = int(message["text"][5:])
        except:
            pass

    if chosen_task_id == -1:
        Facebook.send_message(message["sender_id"], "I did not understand your chose of task")
        return

    tasks = user_states[message["sender_id"]]["tasks"]
    chosen_task = tasks[chosen_task_id - 1]
    questions = chosen_task["questions"]
    data_json = json.loads(chosen_task["content"])

    log(chosen_task)

    # TODO: Duplicate code
    user_states[message["sender_id"]] = {
        "state": "given_task",
        "user_id": user_states[message["sender_id"]]["user_id"],
        "task_id": chosen_task["taskId"],
        "questions": questions,
        "current_question": 0,
        "content_id": chosen_task["contentId"]
    }
    Facebook.send_postback(message["sender_id"], "To cancel this task, click the button. You can also cancel a task by typing 'Cancel'.", "Cancel task", "cancel_task")
    Facebook.send_image(message["sender_id"], data_json["pictureUrl"])
    Facebook.send_message(message["sender_id"], questions[0]["question"])


def handle_message_given_task(message):
    if message["text"] == "Give me a task":
        Facebook.send_message(message["sender_id"], "You already have a task")
        return

    user_state = user_states[message["sender_id"]]

    if message.get("postback") == "cancel_task" or message["text"] == "Cancel":
        user_states[message["sender_id"]] = {
            "state": "idle",
            "user_id": user_state["user_id"]
        }
        Facebook.send_message(message["sender_id"], "Task cancelled!")
        handle_message_idle(message)
        return

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
