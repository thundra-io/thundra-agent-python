import abc
import logging
import time
import traceback
from thundra.opentracing.tracer import ThundraTracer

logger = logging.getLogger(__name__)


class BaseIntegration(abc.ABC):
    def run_and_trace(self, wrapped, instance, args, kwargs):
        tracer = ThundraTracer.get_instance()
        response = None
        exception = None

        scope = tracer.start_active_span(operation_name=self.get_operation_name(wrapped, instance, args, kwargs),
                                         finish_on_close=False)
        # Inject before span tags
        try:
            self.before_call(scope, wrapped, instance, args, kwargs, response, exception)
        except Exception as instrumentation_exception:
            e = {
                'type': str(type(instrumentation_exception)),
                'message': str(instrumentation_exception),
                'traceback': traceback.format_exc(),
                'time': time.time()
            }
            scope.span.set_tag('instrumentation_error', e)

        try:
            # Inform span that initialization completed
            scope.span.on_started()
            # Call original
            response = self.actual_call(wrapped, args, kwargs)
        except Exception as e:
            exception = e

        # Inject after span tags 
        try:
            self.after_call(scope, wrapped, instance, args, kwargs, response, exception)
        except Exception as instrumentation_exception:
            e = {
                'type': str(type(instrumentation_exception)),
                'message': str(instrumentation_exception),
                'traceback': traceback.format_exc(),
                'time': time.time()
            }
            scope.span.set_tag('instrumentation_error', e)

        try:
            scope.span.finish()
        except Exception as e:
            if exception is None:
                exception = e
            else:
                logger.error(e)

        scope.close()

        if exception is not None:
            scope.span.set_error_to_tag(exception)
            raise exception

        return response

    def actual_call(self, wrapped, args, kwargs):
        return wrapped(*args, **kwargs)

    def set_exception(self, exception, traceback_data, span):
        span.set_tag('error.stack', traceback_data)
        span.set_error_to_tag(exception)

    @abc.abstractmethod
    def get_operation_name(self, wrapped, instance, args, kwargs):
        raise Exception("should be implemented")

    @abc.abstractmethod
    def before_call(self, scope, wrapped, instance, args, kwargs, response, exception):
        raise Exception("should be implemented")

    def after_call(self, scope, wrapped, instance, args, kwargs, response, exception):
        if exception is not None:
            self.set_exception(exception, traceback.format_exc(), scope.span)
