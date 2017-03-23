import os

import falcon
from waitress import serve

from api.code.apiserver import add_api_routes, mysql_db
from chatbot.chatbot import add_chatbot_routes

WAITRESS_PORT = '5000'

class PeeweeConnectionMiddleware(object):
    def process_request(self, req, resp):
        mysql_db.connect()

    def process_response(self, req, resp, resource):
        if not mysql_db.is_closed():
            mysql_db.close()


if __name__ == '__main__':
    app = falcon.API(middleware=[PeeweeConnectionMiddleware()])
    add_api_routes(app)
    add_chatbot_routes(app)
    if 'PORT' in os.environ:
        port = os.environ['PORT']
    else:
        port = WAITRESS_PORT
    serve(app, listen='*:' + port)
