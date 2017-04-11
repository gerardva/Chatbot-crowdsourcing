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
    sender_id = message["sender_id"]

    # If we haven't seen the user before, check if the user is registered
    if user_states.get(sender_id) is None:
        get_user(sender_id)

    user_state = user_states[sender_id]  # This should not be None after get_user

    if user_state["state"] == "idle":
        handle_message_idle(message)

    elif user_state["state"] == "given_task_options":
        handle_message_given_task_options(message)

    elif user_state["state"] == "given_task":
        handle_message_given_task(message)

    # Handle default case
    else:
        Facebook.send_message(sender_id, "You ended up in limbo! I'm sorry, I cannot help you at the moment. "
                              "Contact the app creators with the following information: " + user_state["state"])


def handle_message_idle(message):
    sender_id = message["sender_id"]
    user_id = user_states[sender_id]["user_id"]

    # Handle giving task
    if message.get("coordinates") or message.get("quick_reply_payload") == "random_task" or \
       message["text"] == "Random task":
        coordinates = message.get("coordinates", {})
        task = Api.get_random_task(user_id, coordinates.get("long"), coordinates.get("lat"))
        if not task:
            Facebook.send_message(sender_id, "Unfortunately, I could not find a task for you. This most likely means "
                                  "that there are no available tasks at the moment. Be sure to check back later!")
            return

        questions = task["questions"]
        task_content = task["content"]

        send_task(task_content, questions, sender_id, task)

    # Handle giving multiple tasks
    elif message.get("quick_reply_payload") == "list_task" or message["text"] == "List of tasks":
        tasks = Api.get_tasks(user_id)
        if not tasks:
            Facebook.send_message(sender_id, "Sorry, something went wrong when retrieving your task")
            return

        user_states[sender_id] = {
            "state": "given_task_options",
            "user_id": user_id,
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

        Facebook.send_message(sender_id, mes, quick_replies)

    # Handle initial message
    else:  # str.lower(message["text"]) in greetings:
        quick_replies = [{
            "content_type": "location"
        }, {
            "content_type": "text",
            "title": "Random task",
            "payload": "random_task"
        }, {
            "content_type": "text",
            "title": "List of tasks",
            "payload": "list_task"
        }]

        Facebook.send_message(sender_id, "Hey, what do you want to do? I can give you a random task or a list of tasks to choose from. If you send your location "
                                                    "I can give you a task which can be done near you.", quick_replies)


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
    task_content = chosen_task["content"]

    log(chosen_task)
    send_task(task_content, questions, message["sender_id"], chosen_task)


def send_task(task_content, questions, sender_id, task):
    user_states[sender_id] = {
        "state": "given_task",
        "user_id": user_states[sender_id]["user_id"],
        "task_id": task["taskId"],
        "questions": questions,
        "current_question": 0,
        "content_id": task["contentId"]
    }
    Facebook.send_postback(sender_id,
                           "To cancel this task, click the button. You can also cancel a task by typing 'Cancel'.",
                           "Cancel task", "cancel_task")

    data_json = json.loads(task_content) if task_content else {}
    question = questions[0]

    question_text = question["question"]
    #if data_json.get("reviewQuestion") is not None and data_json.get("reviewAnswer") is not None:
    #    question_text = question_text.format(question=data_json.get("reviewQuestion"),
    #                                         answer=data_json.get("reviewAnswer"))

    if data_json.get("pictureUrl") is not None:
        Facebook.send_image(sender_id, data_json["pictureUrl"])

    if data_json.get("question") is not None and data_json.get("answer") is not None:
        Facebook.send_message(sender_id, "Customer tweet:\n" + data_json["question"])
        Facebook.send_message(sender_id, "Webcare answer:\n" + data_json["answer"])

    quick_replies = None
    answer_specification = json.loads(question["answerSpecification"])
    if answer_specification["type"] == "option":
        quick_replies = construct_options_quick_replies(answer_specification["options"])

    Facebook.send_message(sender_id, question_text, quick_replies)


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

    answer_specification = json.loads(questions[current_question]["answerSpecification"])
    answer_type = answer_specification["type"]

    answer = None
    if answer_type == "plaintext":
        if not message["text"]:
            Facebook.send_message(message["sender_id"], "I was expecting text as an answer to this question..")
            return

        answer = message["text"]

    elif answer_type == "image":
        if not message["image"]:
            Facebook.send_message(message["sender_id"], "I was expecting an image as an answer to this question..")
            return

        answer = message["image"]

    elif answer_type == "option":
        if not message["quick_reply_payload"]:
            # Check if answer matches any of the answer_options
            answer_options = answer_specification["options"]
            if message["text"] not in answer_options:
                quick_replies = construct_options_quick_replies(answer_options)
                Facebook.send_message(message["sender_id"],
                                      "I was expecting one of the options as an answer to this question..",
                                      quick_replies)
                return

            answer = message["text"]
        else:
            answer = message["quick_reply_payload"]

    user_id = user_state["user_id"]
    question_id = questions[current_question]["questionId"]
    content_id = user_state["content_id"]

    if current_question == len(questions) - 1:
        res = Api.post_answer(answer, user_id, question_id, content_id, True)
    else:
        res = Api.post_answer(answer, user_id, question_id, content_id, False)

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
        #Facebook.send_message(message["sender_id"], "Thank you for your answer, here comes the next question!")

        answer_specification = json.loads(questions[current_question + 1]["answerSpecification"])
        answer_type = answer_specification["type"]
        quick_replies = None
        if answer_type == "option":
            quick_replies = construct_options_quick_replies(answer_specification["options"])

        Facebook.send_message(message["sender_id"], questions[current_question + 1]["question"], quick_replies)


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


def get_user(sender_id):
    user = Api.get_user(sender_id)
    if not user:
        return False

    if user_states.get(sender_id) is None:
        user_states[sender_id] = {
            "state": "idle",
            "user_id": user["userId"]
        }
