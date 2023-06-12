from catchpoint.context.context_provider import ContextProvider
from catchpoint.context.execution_context import ExecutionContext
from catchpoint.opentracing.tracer import CatchpointTracer


class TracingExecutionContextProvider(ContextProvider):
    def __init__(self):
        self.tracer = CatchpointTracer.get_instance()

    def get(self):
        execution_context = None
        active_span = self.tracer.get_active_span()
        if active_span and hasattr(active_span, 'execution_context'):
            execution_context = active_span.execution_context
        if not execution_context:
            return ExecutionContext()
        return execution_context
    
    def set(self, execution_context):
        active_span = self.tracer.get_active_span()
        if active_span and hasattr(active_span, 'execution_context'):
            active_span.execution_context = execution_context

    def clear(self):
        active_span = self.tracer.get_active_span()
        if active_span and hasattr(active_span, 'execution_context'):
            active_span.execution_context = None

