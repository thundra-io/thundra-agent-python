from thundra.context.context_provider import ContextProvider
from thundra.context.execution_context import ExecutionContext

_execution_context = ExecutionContext()


class GlobalExecutionContextProvider(ContextProvider):
    def get(self):
        return _execution_context

    def set(self, execution_context):
        global _execution_context
        _execution_context = execution_context

    def clear(self):
        global _execution_context
        _execution_context = ExecutionContext()
