from thundra.context.execution_context_manager import ExecutionContextManager


def set_agent_tag(key, value):
    execution_context = ExecutionContextManager.get()
    execution_context.tags[key] = value


def set_many_agent(tags):
    execution_context = ExecutionContextManager.get()
    execution_context.tags.update(tags)


def get_agent_tag(key):
    execution_context = ExecutionContextManager.get()
    if key in execution_context.tags:
        return execution_context.tags[key]
    return None


def get_agent_tags():
    execution_context = ExecutionContextManager.get()
    return execution_context.tags.copy()


def remove_agent_tag(key):
    execution_context = ExecutionContextManager.get()
    return execution_context.tags.pop(key, None)


def set_tag(key, value):
    execution_context = ExecutionContextManager.get()
    execution_context.user_tags[key] = value


def set_tags(tags):
    execution_context = ExecutionContextManager.get()
    execution_context.user_tags.update(tags)


def set_many(tags):
    execution_context = ExecutionContextManager.get()
    execution_context.user_tags.update(tags)


def get_tag(key):
    execution_context = ExecutionContextManager.get()
    if key in execution_context.user_tags:
        return execution_context.user_tags[key]
    return None


def get_tags():
    execution_context = ExecutionContextManager.get()
    return execution_context.user_tags.copy()


def remove_tag(key):
    execution_context = ExecutionContextManager.get()
    return execution_context.user_tags.pop(key, None)


def clear():
    execution_context = ExecutionContextManager.get()
    execution_context.user_tags.clear()
    execution_context.tags.clear()


def clear_error():
    execution_context = ExecutionContextManager.get()
    execution_context.user_error = None


def set_error(err):
    execution_context = ExecutionContextManager.get()
    execution_context.user_error = err


def get_error():
    execution_context = ExecutionContextManager.get()
    return execution_context.user_error
