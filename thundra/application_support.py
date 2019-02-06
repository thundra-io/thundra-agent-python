import sys
import thundra.utils as utils
from thundra import utils, constants

# Get thundra's application related tags
_application_tags = {}
_application_info = {}
application_domain_name = utils.get_configuration(constants.APPLICATION_DOMAIN_NAME_PROP_NAME)
application_class_name = utils.get_configuration(constants.APPLICATION_CLASS_NAME_PROP_NAME)
application_name = utils.get_configuration(constants.APPLICATION_NAME_PROP_NAME)
application_version = utils.get_configuration(constants.APPLICATION_VERSION_PROP_NAME)
application_id = utils.get_configuration(constants.APPLICATION_TAG_PROP_NAME_PREFIX)
application_stage = utils.get_configuration(constants.APPLICATION_STAGE_PROP_NAME)

def parse_application_tags():
    prefix_length = len(constants.APPLICATION_TAG_PROP_NAME_PREFIX)    
    for env_key in utils.get_all_env_variables():
        if env_key.startswith(constants.APPLICATION_TAG_PROP_NAME_PREFIX):
            app_tag_key = env_key[prefix_length:]
            env_val = utils.get_configuration(env_key)
            _application_tags[app_tag_key] = utils.str_to_proper_type(env_val)

def get_application_tags():
    return _application_tags.copy()

def clear_application_tags():
    _application_tags.clear()

def parse_application_info(context):
    _application_info['applicationId'] = application_id if application_id is not None else utils.get_application_id(context)
    _application_info['applicationDomainName'] = application_domain_name if application_domain_name is not None else constants.AWS_LAMBDA_APPLICATION_DOMAIN_NAME
    _application_info['applicationClassName'] = application_class_name if application_class_name is not None else constants.AWS_LAMBDA_APPLICATION_CLASS_NAME
    _application_info['applicationName'] = application_name if application_name is not None else getattr(context, constants.CONTEXT_FUNCTION_NAME, '')
    _application_info['applicationVersion'] = application_version if application_version is not None else getattr(context, constants.CONTEXT_FUNCTION_VERSION, '')
    _application_info['applicationStage'] = application_stage if application_stage is not None else utils.get_configuration(constants.THUNDRA_APPLICATION_STAGE, '')
    _application_info['applicationRuntime'] = 'python'
    _application_info['applicationRuntimeVersion'] = str(sys.version_info[0])
    _application_info['applicationTags'] = get_application_tags()

def get_application_info():
    return _application_info.copy()

# Call parse application tags function to parse application tags
# during the module intialization
parse_application_tags()
