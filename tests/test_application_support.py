import os
import thundra.application_support as application_support

def test_if_can_get_integer_tag(monkeypatch):
    tag_name = 'integerField'
    (env_key, env_val) = (application_support.APPLICATION_TAG_PROP_NAME_PREFIX + tag_name, 3773)
    monkeypatch.setitem(os.environ, env_key, str(env_val))
    application_tags = application_support.parse_application_tags()
    assert application_tags[tag_name] == env_val

def test_if_can_get_float_tag(monkeypatch):
    tag_name = 'floatField'
    (env_key, env_val) = (application_support.APPLICATION_TAG_PROP_NAME_PREFIX + tag_name, 12.3221)
    monkeypatch.setitem(os.environ, env_key, str(env_val))
    application_tags = application_support.parse_application_tags()
    assert application_tags[tag_name] == env_val

def test_if_can_get_string_tag(monkeypatch):
    tag_name = 'stringField'
    (env_key, env_val) = (application_support.APPLICATION_TAG_PROP_NAME_PREFIX + tag_name, 'fooBar')
    monkeypatch.setitem(os.environ, env_key, str(env_val))
    application_tags = application_support.parse_application_tags()
    assert application_tags[tag_name] == env_val