# Chap02/twitter_get_user_timeline.py
import sys
import json
from tweepy import Cursor
from twitter_client import get_twitter_client

i=0

if __name__ == '__main__':
    client = get_twitter_client()
    fname = "search_results.jsonl"
    with open(fname, 'w') as f:
        for page in Cursor(client.search, q='#fruit filter:images').pages(40):
            for status in page:
                if (i<100):
                    data = json.loads(json.dumps(status._json))
                    try: 
                        f.write("{'userId': self.userId,'data': [{'pictureUrl': '"+data["entities"]["media"][0]["media_url"]+"'}],'questionRows': {"\
                            "'q1': 'Is this picture of fruit?',"\
                            "'q2': 'How any dfferent kinds of fruit are visable?'"\
                            "'q3': 'Please select the kinds of fruit that are visable, note multiple selections are alowed?'"\
                            "'q4': 'Please give the number of each kind of fruit'"\
                            "}}))\n")
                        i+=1
                    except KeyError:
                        pass
                #f.write(json.dumps(status._json)+"\n")
