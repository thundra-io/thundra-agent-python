import os
from thundra import constants, application_support

def test_if_can_get_integer_tag(monkeypatch):
    tag_name = 'integerField'
    (env_key, env_val) = (constants.APPLICATION_TAG_PROP_NAME_PREFIX + tag_name, 3773)
    monkeypatch.setitem(os.environ, env_key, str(env_val))
    
    application_support.parse_application_tags()
    application_tags = application_support.get_application_tags()

    assert application_tags[tag_name] == env_val

def test_if_can_get_float_tag(monkeypatch):
    tag_name = 'floatField'
    (env_key, env_val) = (constants.APPLICATION_TAG_PROP_NAME_PREFIX + tag_name, 12.3221)
    monkeypatch.setitem(os.environ, env_key, str(env_val))
    
    application_support.parse_application_tags()
    application_tags = application_support.get_application_tags()

    assert application_tags[tag_name] == env_val

def test_if_can_get_string_tag(monkeypatch):
    tag_name = 'stringField'
    (env_key, env_val) = (constants.APPLICATION_TAG_PROP_NAME_PREFIX + tag_name, 'fooBar')
    monkeypatch.setitem(os.environ, env_key, str(env_val))
    
    application_support.parse_application_tags()
    application_tags = application_support.get_application_tags()

    assert application_tags[tag_name] == env_val

def test_if_can_get_bool_tag(monkeypatch):
    tag_name = 'boolField'
    (env_key, env_val) = (constants.APPLICATION_TAG_PROP_NAME_PREFIX + tag_name, True)
    monkeypatch.setitem(os.environ, env_key, str(env_val))
    
    application_support.parse_application_tags()
    application_tags = application_support.get_application_tags()

    assert application_tags[tag_name] == env_val
