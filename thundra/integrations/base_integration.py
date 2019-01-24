import abc
import logging
import time
import traceback
from thundra.opentracing.tracer import ThundraTracer


class BaseIntegration(abc.ABC):

    CLASS_TYPE = "base"

    def create_span(self, wrapped, instance, args, kwargs):
        tracer = ThundraTracer.get_instance()
        response = None
        exception = None

        scope = tracer.start_active_span(operation_name=self.get_operation_name(), finish_on_close=False)
        try:
            scope.span.on_started()
            response = wrapped(*args, **kwargs)
            return response
        except Exception as e:
            exception = e
            raise e
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
            try:
                scope.span.finish()
            except Exception as injected_err:
                if exception is None:
                    exception = injected_err
            
            scope.close()

            if exception is not None:
                scope.span.set_error_to_tag(exception)
                raise exception
                    
                    


    @abc.abstractmethod
    def get_operation_name(self):
        raise Exception("should be implemented")


    @abc.abstractmethod
    def inject_span_info(self, scope, wrapped, instance, args, kwargs, response, exception):
        raise Exception("should be implemented")