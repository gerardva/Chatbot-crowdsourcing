#!/usr/bin/env python

import os
import json

from twitter import Api

# URL encoded hashtag character is %23
SEARCH_QUERY = '%23crowdsourcing'

CONSUMER_KEY = 'bU8Q4YtVLceidSPnbmzSmzhPa'
# CONSUMER_KEY = os.getenv("CONSUMER_KEY", None)
CONSUMER_SECRET = '4fxYRaphMSmj5SYipWDTxij792mw4bi1pvuWcZ1m0DnuCoYUgc'
# CONSUMER_SECRET = os.getenv("CONSUMER_SECRET", None)
ACCESS_TOKEN = '237870208-sFckbq7hnXDTVhpmgMosxr0jE1aUs3J2Z9sKKXUO'
# ACCESS_TOKEN = os.getenv("ACCESS_TOKEN", None)
ACCESS_TOKEN_SECRET = 'hoSmWLvMhhscPCY6n99qox2P1cdHtXQbz4CTbInQKkk9v'
# ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET", None)

# Languages to filter tweets by is a list. This will be joined by Twitter
# to return data mentioning tweets only in the english language.
LANGUAGES = ['en']

api = Api(CONSUMER_KEY,
          CONSUMER_SECRET,
          ACCESS_TOKEN,
          ACCESS_TOKEN_SECRET)


def main():
    with open('output.txt', 'r+') as f:
        results = api.GetSearch(
            raw_query="q=" + SEARCH_QUERY + "%20filter%3Aimages&count=100")
        f.write(str(results))
        f.truncate()


if __name__ == '__main__':
    main()