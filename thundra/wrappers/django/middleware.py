from thundra import constants
from thundra.context.execution_context_manager import ExecutionContextManager
from thundra.plugins.invocation import invocation_support
from thundra.wrappers.django.django_wrapper import DjangoWrapper, logger


class ThundraMiddleware(object):
    def __init__(self, get_response=None):
        super(ThundraMiddleware, self).__init__()
        self.get_response = get_response
        self._wrapper = DjangoWrapper(disable_log=False)

    def __call__(self, request):
        setattr(request, '_thundra_wrapped', True)
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        before_done = False
        try:
            self._wrapper.before_request(request)
            before_done = True
        except Exception as e:
            logger.error("Error during the before part of Thundra: {}".format(e))

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.
        if before_done:
            try:
                self._wrapper.after_request(response)
            except Exception as e:
                logger.error("Error during the after part of Thundra: {}".format(e))

        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        execution_context = ExecutionContextManager.get()
        if execution_context.scope:
            execution_context.scope.span.operation_name = request.resolver_match.route
            execution_context.trigger_operation_name = request.resolver_match.route
            execution_context.application_resource_name = request.resolver_match.route
            invocation_support.set_agent_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES'],
                                             [request.resolver_match.route])

    def process_exception(self, request, exception):
        self._wrapper.process_exception(exception)
