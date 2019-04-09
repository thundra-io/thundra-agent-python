from thundra import constants

_invocation_tags = {}
function_name = ''

def set_tag(key, value):
    _invocation_tags[key] = value

def set_many(tags):
    _invocation_tags.update(tags)

def get_tag(key):
    if key in _invocation_tags:
        return _invocation_tags[key]
    return None

def get_tags():
    return _invocation_tags.copy()

def remove_tag(key):
    return _invocation_tags.pop(key, None)

def clear():
    _invocation_tags.clear()

def parse_invocation_info(context):
    global function_name
    function_name = getattr(context, constants.CONTEXT_FUNCTION_NAME, '')
