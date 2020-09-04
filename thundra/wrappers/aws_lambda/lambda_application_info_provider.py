import uuid

from thundra import constants, utils
from thundra.application.application_info_provider import ApplicationInfoProvider


class LambdaApplicationInfoProvider(ApplicationInfoProvider):

    def __init__(self):
        log_stream_name = utils.get_env_variable(constants.AWS_LAMBDA_LOG_STREAM_NAME)
        function_version = utils.get_env_variable(constants.AWS_LAMBDA_FUNCTION_VERSION)
        function_name = utils.get_env_variable(constants.AWS_LAMBDA_FUNCTION_NAME)

        application_instance_id = str(uuid.uuid4())
        if log_stream_name and len(log_stream_name.split(']')) >= 2:
            application_instance_id = log_stream_name.split(']')[1]

        self.application_info = {
            'applicationId': '',
            'applicationInstanceId': application_instance_id,
            'applicationName': function_name,
            'applicationVersion': function_version
        }

    def get_application_info(self):
        return self.application_info

    def get_application_tags(self):
        return self.application_info.get('applicationTags', {}).copy()

    @staticmethod
    def get_application_id(context, application_name=None):
        arn = getattr(context, constants.CONTEXT_INVOKED_FUNCTION_ARN, '')
        region = utils.get_aws_region_from_arn(arn)
        if not region:
            region = 'local'
        account_no = 'sam_local' if utils.sam_local_debugging() else utils.get_aws_account_no(arn)
        function_name = application_name if application_name else utils.get_aws_function_name(arn)
        application_id_template = 'aws:lambda:{region}:{account_no}:{function_name}'

        return application_id_template.format(region=region, account_no=account_no, function_name=function_name)

    def update(self, opts):
        filtered_opts = {k: v for k, v in opts.items() if v is not None}
        self.application_info.update(filtered_opts)
