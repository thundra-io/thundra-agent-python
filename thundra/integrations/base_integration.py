import abc
import time
import traceback
from thundra.opentracing.tracer import ThundraTracer


class BaseIntegration(abc.ABC):

    CLASS_TYPE = "base"

    def create_span(self, wrapped, instance, args, kwargs):
        tracer = ThundraTracer.get_instance()
        response = None
        exception = None

        with tracer.start_active_span(operation_name=self.get_operation_name(), finish_on_close=True) as scope:
            try:
                response = wrapped(*args, **kwargs)
                return response
            except Exception as operation_exception:
                exception = operation_exception
                raise
            finally:
                try:
                    self.inject_span_info(scope, wrapped, instance, args, kwargs, response, exception)
                except Exception as instrumentation_exception:
                    error = {
                        'type': str(type(instrumentation_exception)),
                        'message': str(instrumentation_exception),
                        'traceback': traceback.format_exc(),
                        'time': time.time()
                    }
                    scope.span.set_tag('instrumentation_error', error)

    @abc.abstractmethod
    def get_operation_name(self):
        raise Exception("should be implemented")


    @abc.abstractmethod
    def inject_span_info(self, scope, wrapped, instance, args, kwargs, response, exception):
        raise Exception("should be implemented")