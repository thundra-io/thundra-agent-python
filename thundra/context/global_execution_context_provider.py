from thundra.context.execution_context import ExecutionContext

execution_context = ExecutionContext()


class GlobalExecutionContextProvider:
    def get(self):
        return execution_context
