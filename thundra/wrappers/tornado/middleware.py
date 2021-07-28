from thundra.wrappers.tornado.tornado_wrapper import TornadoWrapper, logger


class ThundraMiddleware(object):
    def __init__(self):
        super(ThundraMiddleware, self).__init__()
        self._wrapper = TornadoWrapper()

    def execute(self, handler): 
        try:
            request = handler.request
            self._wrapper.before_request(request)
        except Exception as e:
            logger.error("Error during the before part of Thundra: {}".format(e))

    def finish(self, handler, error=None): 
        try:
            http_response = type('', (object,), {"status_code": handler.get_status()})()
            self._wrapper.after_request(http_response, error)
        except Exception as e:
            logger.error("Error during the after part of Thundra: {}".format(e))
