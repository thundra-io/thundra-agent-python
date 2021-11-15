from thundra.wrappers.flask.flask_wrapper import FlaskWrapper, logger
from thundra.utils import Singleton

class ThundraMiddleware(Singleton):
    def __init__(self):
        self._wrapper = FlaskWrapper()

    def set_app(self, app):
        app.before_request(self.before_request)
        app.after_request(self.after_request)
        app.teardown_request(self.teardown_request)

    def before_request(self):
        try:
            from flask import request
            setattr(request, '_thundra_wrapped', True)
            self._wrapper.before_request(request)
        except Exception as e:
            logger.error("Error during the before part of Thundra: {}".format(e))

    def after_request(self, response):
        try:
            self._wrapper.after_request(response)
        except Exception as e:
            logger.error("Error setting response to context for Thundra: {}".format(e))
        return response

    def teardown_request(self, exception):
        try:
            self._wrapper.teardown_request(exception)
        except Exception as e:
            logger.error("Error during the request teardown of Thundra: {}".format(e))
