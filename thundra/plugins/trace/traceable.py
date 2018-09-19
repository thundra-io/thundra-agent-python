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

    @property
    def trace_args(self):
        return self._trace_args

    @property
    def trace_return_value(self):
        return self._trace_return_value

    @property
    def trace_error(self):
        return self._trace_error

    def __call__(self, original_func):
        @wraps(original_func)
        def trace(*args, **kwargs):
            parent_scope = self.tracer.scope_manager.active
            parent_span = parent_scope.span if parent_scope is not None else None

            scope = self.tracer.start_active_span(original_func.__name__, child_of=parent_span)
            try:
                if self._trace_args is True:
                    function_args_list = []
                    count = 0
                    for arg in args:
                        function_args_dict = {
                            'name': 'arg-' + str(count),
                            'type': type(arg).__name__,
                            'value': arg
                        }
                        count += 1
                        function_args_list.append(function_args_dict)
                    if kwargs is not None:
                        for key, value in kwargs.items():
                            function_args_dict = {
                                'name': key,
                                'type': type(value).__name__,
                                'value': value
                            }
                            function_args_list.append(function_args_dict)
                    scope.span.set_tag('ARGS', function_args_list)
                response = original_func(*args, **kwargs)
                if self._trace_return_value is True and response is not None:
                    return_value = {
                        'type': type(response).__name__,
                        'value': response
                    }
                    scope.span.set_tag('RETURN_VALUE', return_value)
            except Exception as e:
                if self._trace_error is True:
                    scope.span.set_tag('thrownError', type(e).__name__)
                raise e
            finally:
                scope.close()
            return response
        return trace

    call = __call__