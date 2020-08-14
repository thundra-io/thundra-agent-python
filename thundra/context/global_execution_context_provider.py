from thundra.context.execution_context import ExecutionContext

_execution_context = ExecutionContext()


class GlobalExecutionContextProvider:
    def get(self):
        return _execution_context

    def set(self, execution_context):
        global _execution_context
        _execution_context = execution_context
