from catchpoint.application.application_info_provider import ApplicationInfoProvider
from catchpoint.config import config_names
from catchpoint.config.config_provider import ConfigProvider


def test_if_can_get_integer_tag():
    tag_name = 'integerField'
    (env_key, env_val) = (config_names.CATCHPOINT_APPLICATION_TAG_PREFIX + '.' + tag_name, 3773)
    ConfigProvider.set(env_key, str(env_val))

    application_tags = ApplicationInfoProvider.parse_application_tags()

    assert application_tags[tag_name] == env_val


def test_if_can_get_float_tag():
    tag_name = 'floatField'
    (env_key, env_val) = (config_names.CATCHPOINT_APPLICATION_TAG_PREFIX + '.' + tag_name, 12.3221)
    ConfigProvider.set(env_key, str(env_val))

    application_tags = ApplicationInfoProvider.parse_application_tags()

    assert application_tags[tag_name] == env_val


def test_if_can_get_string_tag():
    tag_name = 'stringField'
    (env_key, env_val) = (config_names.CATCHPOINT_APPLICATION_TAG_PREFIX + '.' + tag_name, 'fooBar')
    ConfigProvider.set(env_key, str(env_val))

    application_tags = ApplicationInfoProvider.parse_application_tags()

    assert application_tags[tag_name] == env_val


def test_if_can_get_bool_tag():
    tag_name = 'boolField'
    (env_key, env_val) = (config_names.CATCHPOINT_APPLICATION_TAG_PREFIX + '.' + tag_name, True)
    ConfigProvider.set(env_key, str(env_val))

    application_tags = ApplicationInfoProvider.parse_application_tags()

    assert application_tags[tag_name] == env_val
