import falcon
from waitress import serve

from api.code.apiserver import add_api_routes, mysql_db
from chatbot.chatbot import add_chatbot_routes


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
    serve(app)
