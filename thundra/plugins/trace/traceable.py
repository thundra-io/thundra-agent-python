from functools import wraps

from thundra.opentracing.tracer import ThundraTracer


class Traceable:

    def __init__(self, trace_args=False, trace_return_value=False, trace_error=True):
        self._trace_args = trace_args
        self._trace_return_value = trace_return_value
        self._trace_error = trace_error
        self._tracer = ThundraTracer.getInstance()

    @property
    def tracer(self):
        return self._tracer

    def __call__(self, original_func):
        @wraps(original_func)
        def trace(*args, **kwargs):
            parent_span = self.tracer.get_active_span()
            span = self.tracer.start_span(original_func.__name__, child_of=parent_span)
            try:
                if self._trace_args is True:
                    function_args_list = []
                    count = 0
                    for arg in args:
                        function_args_dict = {
                            'argName': 'arg-' + str(count),
                            'argType': type(arg).__name__,
                            'argValue': arg
                        }
                        count += 1
                        function_args_list.append(function_args_dict)
                    if kwargs is not None:
                        for key, value in kwargs.items():
                            function_args_dict = {
                                'argName': key,
                                'argType': type(value).__name__,
                                'argValue': value
                            }
                            function_args_list.append(function_args_dict)
                    span.set_tag('ARGS', function_args_list)
                response = original_func(*args, **kwargs)
                if self._trace_return_value is True and response is not None:
                    return_value = {
                        'returnValueType': type(response).__name__,
                        'returnValue': response
                    }
                    span.set_tag('RETURN_VALUE', return_value)
            except Exception as e:
                if self._trace_error is True:
                    span.set_tag('thrownError', type(e).__name__)
                raise e
            finally:
                span.finish()
            return response
        return trace
