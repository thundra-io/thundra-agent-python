import math
from thundra import constants, utils

from thundra.plugins.invocation.base_invocation_plugin import BaseInvocationPlugin


class LambdaInvocationPlugin(BaseInvocationPlugin):

    def __init__(self):
        super(LambdaInvocationPlugin, self).__init__()

    def before_invocation_hook(self, plugin_context):
        pass

    def after_invocation_hook(self, plugin_context):
        total_mem, used_mem = utils.process_memory_usage()
        used_mem_in_mb = used_mem / 1048576
        context = plugin_context['context']

        arn = getattr(context, constants.CONTEXT_INVOKED_FUNCTION_ARN, None)

        # Add AWS tags
        self.invocation_data['tags']['aws.region'] = utils.get_aws_region_from_arn(
            getattr(context, constants.CONTEXT_INVOKED_FUNCTION_ARN, None))
        self.invocation_data['tags']['aws.lambda.name'] = getattr(context, constants.CONTEXT_FUNCTION_NAME, None)
        self.invocation_data['tags']['aws.lambda.arn'] = arn
        self.invocation_data['tags']['aws.account_no'] = utils.get_aws_account_no(arn)
        self.invocation_data['tags']['aws.lambda.memory_limit'] = int(
            getattr(context, constants.CONTEXT_MEMORY_LIMIT_IN_MB, 0))
        self.invocation_data['tags']['aws.lambda.log_group_name'] = getattr(context, constants.CONTEXT_LOG_GROUP_NAME,
                                                                            None)
        self.invocation_data['tags']['aws.lambda.log_stream_name'] = getattr(context, constants.CONTEXT_LOG_STREAM_NAME,
                                                                             None)
        self.invocation_data['tags']['aws.lambda.invocation.coldstart'] = self.invocation_data['coldStart']
        self.invocation_data['tags']['aws.lambda.invocation.timeout'] = plugin_context.get('timeout', False)
        self.invocation_data['tags']['aws.lambda.invocation.request_id'] = getattr(context,
                                                                                   constants.CONTEXT_AWS_REQUEST_ID,
                                                                                   None)
        self.invocation_data['tags']['aws.lambda.invocation.memory_usage'] = math.floor(used_mem_in_mb)

        xray_info = utils.parse_x_ray_trace_info()
        if xray_info.get("trace_id"):
            self.invocation_data['tags']['aws.xray.trace.id'] = xray_info.get("trace_id")
        if xray_info.get("segment_id"):
            self.invocation_data['tags']['aws.xray.segment.id'] = xray_info.get("segment_id")
