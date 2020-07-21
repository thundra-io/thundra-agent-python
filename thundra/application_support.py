import sys
from thundra import utils, constants

from thundra.config.config_provider import ConfigProvider
from thundra.config import config_names

# Get thundra's application related tags
_application_tags = {}
_application_info = {}
application_domain_name = ConfigProvider.get(config_names.THUNDRA_APPLICATION_DOMAIN_NAME)
application_class_name = ConfigProvider.get(config_names.THUNDRA_APPLICATION_CLASS_NAME)
application_name = ConfigProvider.get(config_names.THUNDRA_APPLICATION_NAME)
application_version = ConfigProvider.get(config_names.THUNDRA_APPLICATION_VERSION)
application_id = ConfigProvider.get(config_names.THUNDRA_APPLICATION_TAG_PREFIX)
application_stage = ConfigProvider.get(config_names.THUNDRA_APPLICATION_STAGE)

def parse_application_tags():
    prefix_length = len(config_names.THUNDRA_APPLICATION_TAG_PREFIX)
    for key in ConfigProvider.configs:
        if key.startswith(config_names.THUNDRA_APPLICATION_TAG_PREFIX):
            app_tag_key = key[prefix_length:]
            val = ConfigProvider.get(key)
            _application_tags[app_tag_key] = val

def get_application_tags():
    return _application_tags.copy()

def clear_application_tags():
    _application_tags.clear()

def parse_application_info(context):
    _application_info['applicationId'] = application_id if application_id is not None else utils.get_application_id(context)
    _application_info['applicationInstanceId'] = utils.get_application_instance_id(context)
    _application_info['applicationDomainName'] = application_domain_name if application_domain_name is not None else constants.AWS_LAMBDA_APPLICATION_DOMAIN_NAME
    _application_info['applicationClassName'] = application_class_name if application_class_name is not None else constants.AWS_LAMBDA_APPLICATION_CLASS_NAME
    _application_info['applicationName'] = application_name if application_name is not None else getattr(context, constants.CONTEXT_FUNCTION_NAME, '')
    _application_info['applicationVersion'] = application_version if application_version is not None else getattr(context, constants.CONTEXT_FUNCTION_VERSION, '')
    _application_info['applicationStage'] = application_stage if application_stage is not None else ConfigProvider.get(config_names.THUNDRA_APPLICATION_STAGE, '')
    _application_info['applicationRuntime'] = 'python'
    _application_info['applicationRuntimeVersion'] = str(sys.version_info[0])
    _application_info['applicationTags'] = get_application_tags()

def get_application_info():
    return _application_info.copy()

# Call parse application tags function to parse application tags
# during the module intialization
parse_application_tags()
