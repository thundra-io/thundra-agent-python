import json
from functools import wraps

from thundra.opentracing.tracer import ThundraTracer
from thundra.serializable import Serializable


class Traceable:

    def __init__(self, trace_args=False, trace_return_value=False, trace_error=True):
        self._trace_args = trace_args
        self._trace_return_value = trace_return_value
        self._trace_error = trace_error
        self._tracer = ThundraTracer.get_instance()

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

    def __is_serializable__(self, value):
        return value is None or isinstance(value, (str, int, float, bool))

    def __serialize_value__(self, value):
        if self.__is_serializable__(value):
            return value
        elif isinstance(value, Serializable):
            return value.serialize()
        else:
            try:
                # Check whether object is serializable
                json.dumps(value)
                return value
            except TypeError:
                return 'Unable to serialize the object'

    def __call__(self, original_func):
        @wraps(original_func)
        def trace(*args, **kwargs):
            parent_scope = self.tracer.scope_manager.active
            parent_span = parent_scope.span if parent_scope is not None else None

            # Set finish_on_close to False, otherwise it calls span's finish method which can raise an error,
            # which would cause the scope left open  
            scope = self.tracer.start_active_span(original_func.__name__, child_of=parent_span, finish_on_close=False)
            scope.span.class_name = 'Method'
            traced_err = None
            try:
                # Add argument related tags to the span before calling original method
                if self._trace_args is True:
                    function_args_list = []
                    count = 0
                    for arg in args:
                        function_args_dict = {
                            'name': 'arg-' + str(count),
                            'type': type(arg).__name__,
                            'value': self.__serialize_value__(arg)
                        }
                        count += 1
                        function_args_list.append(function_args_dict)
                    if kwargs is not None:
                        for key, value in kwargs.items():
                            function_args_dict = {
                                'name': key,
                                'type': type(value).__name__,
                                'value': self.__serialize_value__(value)
                            }
                            function_args_list.append(function_args_dict)
                    scope.span.set_tag('method.args', function_args_list)
                # Inform that span is initalized
                scope.span.on_started()
                # Call original func
                response = original_func(*args, **kwargs)
                # Add return value related tags after having called the original func
                if self._trace_return_value is True and response is not None:
                    return_value = {
                        'type': type(response).__name__,
                        'value': self.__serialize_value__(response)
                    }
                    scope.span.set_tag('method.return_value', return_value)
            except Exception as e:
                if self._trace_error is True:
                    traced_err = e
                raise e
            finally:
                try:
                    # Since span's finish method calls listeners, it can raise an error
                    scope.span.finish()
                except Exception as injected_err:
                    if traced_err is None:
                        traced_err = injected_err
                # Close the scope regardless of an error is raised or not
                scope.close()
                # Set the error tags to the span (if any)
                if traced_err is not None:
                    scope.span.set_error_to_tag(traced_err)
                    raise traced_err
            return response

        return trace

    call = __call__
