_tags = {}

def set_tag(key, value):
    _tags[key] = value

def set_many(tags):
    _tags.update(tags)

def get_tag(key):
    if key in _tags:
        return _tags[key]
    return None

def get_tags_dict():
    return _tags.copy()

def remove_tag(key):
    return _tags.pop(key, None)

def clear():
    _tags.clear()