from thundra import constants

_invocation_tags = {}
_user_invocation_tags = {}
_user_error = None
function_name = ''

def set_agent_tag(key, value):
    _invocation_tags[key] = value

def set_many_agent(tags):
    _invocation_tags.update(tags)

def get_agent_tag(key):
    if key in _invocation_tags:
        return _invocation_tags[key]
    return None

def get_agent_tags():
    return _invocation_tags.copy()

def remove_agent_tag(key):
    return _invocation_tags.pop(key, None)

def set_tag(key, value):
    _user_invocation_tags[key] = value

def set_many(tags):
    _user_invocation_tags.update(tags)

def get_tag(key):
    if key in _user_invocation_tags:
        return _user_invocation_tags[key]
    return None

def get_tags():
    return _user_invocation_tags.copy()

def remove_tag(key):
    return _user_invocation_tags.pop(key, None)

def clear():
    _invocation_tags.clear()
    _user_invocation_tags.clear()

def clear_error():
    global _user_error
    _user_error = None

def set_error(err):
    global _user_error
    _user_error = err

def get_error():
    return _user_error

def parse_invocation_info(context):
    global function_name
    function_name = getattr(context, constants.CONTEXT_FUNCTION_NAME, '')
