import inspect
import sys
from functools import wraps
from threading import Lock

import jsonpickle
from opentracing import Scope

from thundra import constants
from thundra.opentracing.tracer import ThundraTracer
from thundra.plugins.log.thundra_logger import debug_logger
from thundra.serializable import Serializable
from pympler import asizeof
import threading
trace_local = threading.local()

DATA_LIMIT = 8 * 1024 # 8KB
DATA_LIMIT_RETURN_STR = "[THUNDRA] Data is over {} KB".format(DATA_LIMIT / 1024)
METHOD_LINES_LIMIT = 100
SERIALIZATION_DEPTH=1

def __get_traceable_from_back_frame(frame):
    _back_frame = frame.f_back
    if _back_frame and 'self' in _back_frame.f_locals:
        _self = _back_frame.f_locals['self']
        if isinstance(_self, Traceable):
            return _self
    return None


def __get_funcname_from_back_frame(frame):
    _back_frame = frame.f_back
    if _back_frame and 'original_func' in _back_frame.f_locals:
        _func = _back_frame.f_locals['original_func']
        return _func.__name__
    return None


def __get_scope_from_back_frame(frame):
    _back_frame = frame.f_back
    if _back_frame and 'scope' in _back_frame.f_locals:
        _scope = _back_frame.f_locals['scope']
        if isinstance(_scope, Scope):
            return _scope
    return None


def trace_lines(frame, event, arg):
    if event != 'line':
        return
    _line_no = frame.f_lineno

    _trace_local_variables_ = False
    _trace_lines_with_source = False
    _scope = __get_scope_from_back_frame(frame)

    if not _scope or not _scope.span:
        return

    _traceable = __get_traceable_from_back_frame(frame)
    if _traceable == None:
        return
    _trace_local_variables_ = _traceable._trace_local_variables
    _trace_lines_with_source = _traceable._trace_lines_with_source

    method_lines_list = _scope.span.get_tag(constants.LineByLineTracingTags['lines'])
    if method_lines_list != None and len(method_lines_list) >= METHOD_LINES_LIMIT:
        return
    _local_vars = []
    global DATA_LIMIT, DATA_LIMIT_RETURN_STR, SERIALIZATION_DEPTH
    if _trace_local_variables_:
        pickler = jsonpickle.pickler.Pickler(max_depth=SERIALIZATION_DEPTH)
        for l in frame.f_locals:
            _local_var_value = frame.f_locals[l]
            _local_var_type = type(_local_var_value).__name__
            if asizeof.asizeof(_local_var_value, limit=SERIALIZATION_DEPTH) > DATA_LIMIT:
                _local_var_value = DATA_LIMIT_RETURN_STR
            else:
                try:
                    _local_var_value = pickler.flatten(_local_var_value, reset=True)
                except Exception as e:
                    _local_var_value = '<not-json-serializable-object>'
            _local_var = {
                'name': l,
                'value': _local_var_value,
                'type': _local_var_type
            }
            _local_vars.append(_local_var)

    method_line = {
        'line': _line_no,
        'localVars': _local_vars
    }
    if not method_lines_list:
        method_lines_list = []
    method_lines_list.append(method_line)
    _scope.span.set_tag(constants.LineByLineTracingTags['lines'], method_lines_list)
    

def trace_calls(frame, event, arg):
    if not trace_local.trace_call_active:
        return

    trace_local.trace_call_active = False

    # First check whether current call is wrapped
    wrapped_by_thundra = frame.f_back and frame.f_back.f_code.co_name == '___thundra_trace___'
    if not wrapped_by_thundra:
        return

    # Note that "is Thundra wrapped check" is applied before "is event call" check.
    # Because most of the time "is Thundra wrapped check" is false but "is event call" is true.
    # And since most of the time 'trace_calls' will return 'None',
    # it is better to detect false case with less comparison.

    # Only handle 'call' events
    if event != 'call':
        return

    _func_name = frame.f_code.co_name
    # Ignore
    # - 'write()' calls from print statements
    # - Thundra trace decorator calls
    ignored = _func_name == 'write' or _func_name == '___thundra_trace___'
    if ignored:
        return

    _traceable = None
    try:
        _traceable = __get_traceable_from_back_frame(frame)
    except ValueError:
        pass
    if not _traceable or not _traceable.trace_line_by_line:
        return

    orig_func_name = __get_funcname_from_back_frame(frame)
    if _func_name == orig_func_name:
        return trace_lines


# To keep track of the active line-by-line traced Tracable count
_lock = Lock()
_line_traced_count = 0

class Traceable:

    def __init__(self,
                 trace_args=None, trace_return_value=None, trace_error=True,
                 trace_line_by_line=False, trace_lines_with_source=None, trace_local_variables=None):
        self._trace_args = trace_args
        if trace_args is None:
            self._trace_args = False

        self._trace_return_value = trace_return_value
        if trace_return_value is None:
            self._trace_return_value = False

        self._trace_lines_with_source = trace_lines_with_source
        if trace_lines_with_source is None:
            self._trace_lines_with_source = False

        self._trace_local_variables = trace_local_variables
        if trace_local_variables is None:
            self._trace_local_variables = False

        self._trace_error = trace_error
        self._trace_line_by_line = trace_line_by_line

        if trace_line_by_line:
            if trace_lines_with_source is None:
                self._trace_lines_with_source = True
            if trace_return_value is None:
                self._trace_return_value = True
            if trace_local_variables is None:
                self._trace_local_variables = True
            if trace_args is None:
                self._trace_args = True

        self._tracing = False
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

    @property
    def trace_line_by_line(self):
        return self._trace_line_by_line

    @property
    def trace_lines_with_source(self):
        return self._trace_lines_with_source

    @property
    def trace_local_variables(self):
        return self._trace_local_variables

    def __is_serializable__(self, value):
        return value is None or isinstance(value, (str, int, float, bool))

    def __serialize_value__(self, value):
        global DATA_LIMIT, DATA_LIMIT_RETURN_STR, SERIALIZATION_DEPTH
        value_size = asizeof.asizeof(value, limit=SERIALIZATION_DEPTH)
        if value_size > DATA_LIMIT:
            return DATA_LIMIT_RETURN_STR, type(value).__name__
        if self.__is_serializable__(value):
            return value, type(value).__name__
        elif isinstance(value, Serializable):
            return value.serialize(), type(value).__name__
        try:
            pickler = jsonpickle.pickler.Pickler(max_depth=SERIALIZATION_DEPTH)
            value_dict = pickler.flatten(value, reset=True)
            return value_dict, type(value).__name__
        except:
            return '<not-json-serializable-object>', type(value).__name__

    def __call__(self, original_func):
        @wraps(original_func)
        def ___thundra_trace___(*args, **kwargs):
            parent_scope = self.tracer.scope_manager.active
            parent_span = parent_scope.span if parent_scope is not None else None

            # Set finish_on_close to False, otherwise it calls span's finish method which can raise an error,
            # which would cause the scope left open  
            scope = self.tracer.start_active_span(original_func.__name__, child_of=parent_span, finish_on_close=False)
            scope.span.class_name = 'Method'
            traced_err = None
            global _line_traced_count
            global DATA_LIMIT
            
            try:
                # Add argument related tags to the span before calling original method
                if self._trace_args is True:
                    function_args_list = []
                    count = 0
                    for arg in args:
                        value, value_type = self.__serialize_value__(arg)
                        function_args_dict = {
                            'name': 'arg-' + str(count),
                            'type': value_type,
                            'value': value
                        }
                        count += 1
                        function_args_list.append(function_args_dict)
                    if kwargs is not None:
                        for key, value in kwargs.items():
                            value, value_type = self.__serialize_value__(value)
                            function_args_dict = {
                                'name': key,
                                'type': value_type,
                                'value': value
                            }
                            function_args_list.append(function_args_dict)
                    scope.span.set_tag(constants.LineByLineTracingTags['args'], function_args_list)
                # Inform that span is initalized
                scope.span.on_started()
                self._tracing = True
                # Check if line-by-line tracing enabled
                if self.trace_line_by_line:
                    try:
                        if self.trace_lines_with_source:
                            source_lines, start_line = inspect.getsourcelines(original_func)
                            scope.span.set_tag(constants.LineByLineTracingTags['source'], ''.join(source_lines))
                            scope.span.set_tag(constants.LineByLineTracingTags['start_line'], start_line)
                    except Exception as e:
                        debug_logger("Cannot get source code in traceable: " + str(e))
                    with _lock:
                        if _line_traced_count == 0:
                            sys.settrace(trace_calls)
                        _line_traced_count += 1

                trace_local.trace_call_active = True
                # Call original func
                response = original_func(*args, **kwargs)
                self._tracing = False
                # Add return value related tags after having called the original func
                if self._trace_return_value is True and response is not None:
                    value, value_type = self.__serialize_value__(response)
                    return_value = {
                        'type': value_type,
                        'value': value
                    }
                    scope.span.set_tag('method.return_value', return_value)
            except Exception as e:
                if self._trace_error is True:
                    traced_err = e
                raise e
            finally:
                self._tracing = False
                # Disable line-by-line tracing if it is not used
                if self._trace_line_by_line:
                    with _lock:
                        _line_traced_count -= 1
                        if _line_traced_count == 0:
                            sys.settrace(None)

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

        return ___thundra_trace___

    call = __call__
