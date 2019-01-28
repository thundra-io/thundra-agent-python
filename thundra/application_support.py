import thundra.utils as utils
from thundra.constants import (
    APPLICATION_ID_PROP_NAME,
    APPLICATION_DOMAIN_NAME_PROP_NAME,
    APPLICATION_CLASS_NAME_PROP_NAME,
    APPLICATION_NAME_PROP_NAME,
    APPLICATION_VERSION_PROP_NAME,
    APPLICATION_STAGE_PROP_NAME,
    APPLICATION_TAG_PROP_NAME_PREFIX,
)

# Get thundra's application related tags
_application_tags = {}
application_domain_name = utils.get_configuration(APPLICATION_DOMAIN_NAME_PROP_NAME)
application_class_name = utils.get_configuration(APPLICATION_CLASS_NAME_PROP_NAME)
application_name = utils.get_configuration(APPLICATION_NAME_PROP_NAME)
application_version = utils.get_configuration(APPLICATION_VERSION_PROP_NAME)
application_id = utils.get_configuration(APPLICATION_ID_PROP_NAME)
application_stage = utils.get_configuration(APPLICATION_STAGE_PROP_NAME)

def parse_application_tags():
    prefix_length = len(APPLICATION_TAG_PROP_NAME_PREFIX)
    for env_key in utils.get_all_env_variables():
        if env_key.startswith(APPLICATION_TAG_PROP_NAME_PREFIX):
            app_tag_key = env_key[prefix_length:]
            env_val = utils.get_configuration(env_key)
            _application_tags[app_tag_key] = utils.str_to_proper_type(env_val)

def get_application_tags():
    return _application_tags.copy()

def clear_application_tags():
    _application_tags.clear()

# Call parse application tags function to parse application tags
# during the module intialization
parse_application_tags()
