from thundra import constants, utils
from thundra.application.application_info_provider import ApplicationInfoProvider


class LambdaApplicationInfoProvider(ApplicationInfoProvider):
    application_info = {}

    def get_application_info(self):
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

    def update(self, opts):
        filtered_opts = {k: v for k, v in opts.items() if v is not None}
        self.application_info.update(filtered_opts)
