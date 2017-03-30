import requests
import os
from chatbot.logger import log

def facebook_send(data):
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
