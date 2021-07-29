import tornado.web

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")

class QueryHandler(tornado.web.RequestHandler):
    def get(self):
        query_arg = self.get_query_argument("foo")
        self.write(query_arg)

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/query", QueryHandler),
    ])