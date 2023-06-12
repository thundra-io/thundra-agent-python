from catchpoint.context.execution_context_manager import ExecutionContextManager
from catchpoint.wrappers.django.django_wrapper import DjangoWrapper, logger
from catchpoint.wrappers.web_wrapper_utils import process_request_route


class CatchpointMiddleware(object):
    def __init__(self, get_response=None):
        super(CatchpointMiddleware, self).__init__()
        self.get_response = get_response
        self._wrapper = DjangoWrapper()

    def __call__(self, request):
        setattr(request, '_catchpoint_wrapped', True)
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        before_done = False
        try:
            self._wrapper.before_request(request)
            before_done = True
        except Exception as e:
            logger.error("Error during the before part of Catchpoint: {}".format(e))

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.
        if before_done:
            try:
                self._wrapper.after_request(response)
            except Exception as e:
                logger.error("Error during the after part of Catchpoint: {}".format(e))

        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        execution_context = ExecutionContextManager.get()
        if request.resolver_match:
            request_host = request.get_host().split(':')[0]
            import sys
            if sys.version_info[0] >= 3:
                process_request_route(execution_context, request.resolver_match.route, request_host)
            else:
                process_request_route(execution_context, request.resolver_match.url_name, request_host)
            
    def process_exception(self, request, exception):
        self._wrapper.process_exception(exception)
