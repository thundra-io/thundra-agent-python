import time
import traceback
from thundra.opentracing.tracer import ThundraTracer


class BaseIntegrationFactory(object):

    @staticmethod
    def create_span(wrapped, instance, args, kwargs, operation_name, integration_class):
        tracer = ThundraTracer.get_instance()
        response = None
        exception = None
        with tracer.start_active_span(operation_name=operation_name, finish_on_close=True) as scope:
            try:
                response = wrapped(*args, **kwargs)
                return response
            except Exception as operation_exception:
                exception = operation_exception
                raise
            finally:
                try:
                    integration_class().inject_span_info(
                        scope,
                        wrapped,
                        instance,
                        args,
                        kwargs,
                        response,
                        exception
                    )
                except Exception as instrumentation_exception:
                    error = {
                        'type': str(type(instrumentation_exception)),
                        'message': str(instrumentation_exception),
                        'traceback': traceback.format_exc(),
                        'time': time.time()
                    }
                    scope.span.set_tag('instrumentation_error', error)

