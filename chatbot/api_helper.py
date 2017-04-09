import requests
from chatbot.logger import log

api_url = "http://localhost:5000"  # no trailing slash
api_methods = {
    'GET': requests.get,
    'POST': requests.post,
    'PUT': requests.put
}


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


def get_tasks():
    res = call_api("GET", "/worker/tasks?order=random&limit=3")

    if not res:
        return False

    return res


def post_answer(answer, user_id, question_id, content_id):
    data = {
        "answer": answer,
        "userId": user_id,
        "questionId": question_id,
        "contentId": content_id
    }

    res = call_api("POST", "/worker/answers", data)
    if not res:
        return False

    return True

def get_user(facebook_id):
    data = {
        'facebookId': facebook_id
    }

    res = call_api("POST", "/worker/users", data)
    if not res:
        return False

    return res