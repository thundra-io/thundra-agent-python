from functools import wraps

from thundra.opentracing.tracer import ThundraTracer
from thundra.serializable import Serializable


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
            scope.span.set_tag('error', False)
            try:
                if self._trace_args is True:
                    function_args_list = []
                    count = 0
                    for arg in args:
                        argument = arg
                        if hasattr(arg, '__dict__'):
                            if isinstance(arg, Serializable):
                                argument = arg.serialize()
                            else:
                                argument = 'Not json serializable object'
                        function_args_dict = {
                            'argName': 'arg-' + str(count),
                            'argType': type(arg).__name__,
                            'argValue': argument
                        }
                        count += 1
                        function_args_list.append(function_args_dict)
                    if kwargs is not None:
                        for key, value in kwargs.items():
                            argument = value
                            if '__dict__' in value.__dir__():
                                argument = value.__dict__
                            function_args_dict = {
                                'argName': key,
                                'argType': type(value).__name__,
                                'argValue': argument
                            }
                            function_args_list.append(function_args_dict)
                    scope.span.set_tag('ARGS', function_args_list)
                response = original_func(*args, **kwargs)
                if self._trace_return_value is True and response is not None:
                    resp = response
                    if hasattr(response, '__dict__'):
                        if isinstance(response, Serializable):
                            resp = response.serialize()
                        else:
                            resp = 'Not json serializable object'
                    return_value = {
                        'returnValueType': type(response).__name__,
                        'returnValue': resp
                    }
                    scope.span.set_tag('RETURN_VALUE', return_value)
            except Exception as e:
                if self._trace_error is True:
                    scope.span.set_error_to_tag(e)
                raise e
            finally:
                scope.close()
            return response
        return trace

    call = __call__