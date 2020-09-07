from thundra.context.context_provider import ContextProvider
from thundra.context.execution_context import ExecutionContext
from thundra.opentracing.tracer import ThundraTracer


class TracingExecutionContextProvider(ContextProvider):
    def __init__(self):
        self.tracer = ThundraTracer.get_instance()

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

