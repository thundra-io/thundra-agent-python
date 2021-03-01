from thundra.context.execution_context_manager import ExecutionContextManager
from thundra.wrappers.web_wrapper_utils import process_request_route
from thundra.wrappers.tornado.tornado_wrapper import TornadoWrapper, logger

class ThundraMiddleware(object):
    def __init__(self, wrapped, instance):
        super(ThundraMiddleware, self).__init__()
        self._wrapped = wrapped
        self._instance = instance
        self._wrapper = TornadoWrapper()

    async def _execute(self, args, kwargs) -> None:
        setattr(self._instance.request, '_thundra_wrapped', True)

        # Code to be executed for each request before
        # the view (and later middleware) are called.
        before_done = False
        try:
            self._wrapper.before_request(self._instance.request)
            before_done = True
        except Exception as e:
            logger.error("Error during the before part of Thundra: {}".format(e))

        result = self._wrapped(*args, **kwargs)
        if result is not None:
            result = await result

        # Code to be executed for each request/response after
        # the view is called.
        if before_done:
            try:
                http_response = type('',(object,),{"status_code": self._instance._status_code})()
                self._wrapper.after_request(http_response)
            except Exception as e:
                logger.error("Error during the after part of Thundra: {}".format(e))
