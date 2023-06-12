from functools import wraps
from catchpoint.opentracing.tracer import CatchpointTracer


class TraceAwareWrapper:

    def __init__(self, active_span=None):
        if active_span is None:
            active_scope = CatchpointTracer.get_instance().scope_manager.active
            active_span = active_scope.span if active_scope is not None else None
        self._parent_span = active_span

    @property
    def parent_span(self):
        return self._parent_span

    def __call__(self, original_func):
        @wraps(original_func)
        def wrapper(*args, **kwargs):
            CatchpointTracer.get_instance().scope_manager.activate(self.parent_span, True)
            return original_func(*args, **kwargs)
        return wrapper
