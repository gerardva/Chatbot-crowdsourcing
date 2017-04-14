import sys


def log(message):  # simple wrapper for logging to stdout on heroku
    try:
        print(str(message))
        sys.stdout.flush()
    except:
        print("Error while logging")
