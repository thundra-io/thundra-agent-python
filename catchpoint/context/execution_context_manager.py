from catchpoint.context.execution_context import ExecutionContext
from catchpoint.context.global_execution_context_provider import GlobalExecutionContextProvider


class ExecutionContextManager:
    context_provider = None

    @staticmethod
    def set_provider(provider):
        ExecutionContextManager.context_provider = provider

    @staticmethod
    def set(context):
        ExecutionContextManager.context_provider.set(context)

    @staticmethod
    def clear():
        ExecutionContextManager.context_provider.clear()

    @staticmethod
    def get():
        if not ExecutionContextManager.context_provider:
            return ExecutionContext()
        execution_context = ExecutionContextManager.context_provider.get()
        if not execution_context:
            return ExecutionContext()
        return execution_context
