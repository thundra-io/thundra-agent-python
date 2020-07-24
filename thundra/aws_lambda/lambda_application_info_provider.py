import sys

from thundra.application.application_info_provider import ApplicationInfoProvider
from thundra.config.config_provider import ConfigProvider
from thundra.config import config_names
from thundra import constants, utils
from thundra.aws_lambda.lambda_context_provider import LambdaContextProvider


class LambdaApplicationInfoProvider(ApplicationInfoProvider):
    application_info = {}

    def __init__(self):
        self.application_info['applicationId'] = ConfigProvider.get(config_names.THUNDRA_APPLICATION_TAG_PREFIX)
        self.application_info['applicationDomainName'] = ConfigProvider.get(
            config_names.THUNDRA_APPLICATION_DOMAIN_NAME)
        self.application_info['applicationClassName'] = ConfigProvider.get(config_names.THUNDRA_APPLICATION_CLASS_NAME)
        self.application_info['applicationName'] = ConfigProvider.get(config_names.THUNDRA_APPLICATION_NAME)
        self.application_info['applicationVersion'] = ConfigProvider.get(config_names.THUNDRA_APPLICATION_VERSION)
        self.application_info['applicationStage'] = ConfigProvider.get(config_names.THUNDRA_APPLICATION_STAGE, '')
        self.application_info['applicationRuntime'] = 'python'
        self.application_info['applicationRuntimeVersion'] = str(sys.version_info[0])
        self.application_info['applicationTags'] = ApplicationInfoProvider.parse_application_tags()

    def get_application_info(self):
        context = LambdaContextProvider.get_context()
        self.application_info['applicationInstanceId'] = LambdaApplicationInfoProvider.get_application_instance_id(
            context)

        if self.application_info['applicationId'] is None:
            self.application_info['applicationId'] = LambdaApplicationInfoProvider.get_application_id(context)

        if self.application_info['applicationName'] is None:
            self.application_info['applicationName'] = getattr(context, constants.CONTEXT_FUNCTION_NAME, '')

        if self.application_info['applicationVersion'] is None:
            self.application_info['applicationVersion'] = getattr(context, constants.CONTEXT_FUNCTION_VERSION, '')

        return self.application_info.copy()

    def get_application_tags(self):
        return self.application_info.get('applicationTags', {}).copy()

    @staticmethod
    def get_application_instance_id(context):
        aws_lambda_log_stream_name = getattr(context, constants.CONTEXT_LOG_STREAM_NAME, '')
        try:
            return aws_lambda_log_stream_name.split(']')[1]
        except:
            return ''

    @staticmethod
    def get_application_id(context):
        arn = getattr(context, constants.CONTEXT_INVOKED_FUNCTION_ARN, '')
        region = utils.get_aws_region_from_arn(arn)
        account_no = 'sam_local' if utils.sam_local_debugging() else utils.get_aws_account_no(arn)
        function_name = utils.get_aws_funtion_name(arn)
        application_id_template = 'aws:lambda:{region}:{account_no}:{function_name}'

        return application_id_template.format(region=region, account_no=account_no, function_name=function_name)
