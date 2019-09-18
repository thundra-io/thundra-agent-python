import logging

from thundra.plugins.invocation import invocation_support
from thundra.plugins.log.thundra_logger import debug_logger
from thundra import utils, constants, lambda_event_utils, config
from thundra.plugins.trace.base_trace_plugin import BaseTracePlugin

logger = logging.getLogger(__name__)


class LambdaTracePlugin(BaseTracePlugin):

    def __init__(self):
        super(LambdaTracePlugin, self).__init__()

    def before_trace_hook(self, plugin_context):
        context = plugin_context['context']

        # Set root span class and domain names
        self.root_span.class_name = constants.ClassNames['LAMBDA']
        self.root_span.domain_name = constants.DomainNames['API']

        self.root_span.set_tag('aws.region', utils.get_aws_region_from_arn(
            getattr(context, constants.CONTEXT_INVOKED_FUNCTION_ARN, None)))
        self.root_span.set_tag('aws.lambda.name', invocation_support.function_name)
        self.root_span.set_tag('aws.lambda.arn', getattr(context, constants.CONTEXT_INVOKED_FUNCTION_ARN, None))
        self.root_span.set_tag('aws.lambda.memory.limit', getattr(context, constants.CONTEXT_MEMORY_LIMIT_IN_MB, None))
        self.root_span.set_tag('aws.lambda.log_group_name', getattr(context, constants.CONTEXT_LOG_GROUP_NAME, None))
        self.root_span.set_tag('aws.lambda.log_stream_name', getattr(context, constants.CONTEXT_LOG_STREAM_NAME, None))
        self.root_span.set_tag('aws.lambda.invocation.coldstart', constants.REQUEST_COUNT == 1)
        self.root_span.set_tag('aws.lambda.invocation.timeout', plugin_context.get('timeout', False))
        self.root_span.set_tag('aws.lambda.invocation.request_id',
                               getattr(context, constants.CONTEXT_AWS_REQUEST_ID, None))
        self._inject_trigger_tags(self.root_span, plugin_context['request'], context)

    def after_trace_hook(self, plugin_context):
        trigger_class_name = self.root_span.get_tag(constants.SpanTags['TRIGGER_CLASS_NAME'])

        # Disable request data sending for cloudwatchlog, firehose and kinesis if not
        # enabled by configuration because requests can get too big for these
        enable_request_data = True
        if (
                trigger_class_name == constants.ClassNames['CLOUDWATCHLOG'] and
                not config.enable_trace_cloudwatchlog_request()) or (

                trigger_class_name == constants.ClassNames['FIREHOSE'] and
                not config.enable_trace_firehose_request()) or (

                trigger_class_name == constants.ClassNames['KINESIS'] and
                not config.enable_trace_kinesis_request()
        ):
            enable_request_data = False

        # ADDING TAGS #
        if (not config.skip_trace_request()) and enable_request_data:
            self.root_span.set_tag('aws.lambda.invocation.request', plugin_context.get('request', None))
        if not config.skip_trace_response():
            self.root_span.set_tag('aws.lambda.invocation.response', plugin_context.get('response', None))

        if trigger_class_name == constants.ClassNames['APIGATEWAY']:
            self.process_api_gw_response(plugin_context)

    def process_api_gw_response(self, plugin_context):
        try:
            if plugin_context.get('response'):
                if not plugin_context.get('response', {}).get('headers'):
                    plugin_context['response']['headers'] = {}

                plugin_context['response']['headers'][constants.TRIGGER_RESOURCE_NAME_TAG] = plugin_context['request'][
                    'resource']
        except:
            pass

    @staticmethod
    def _inject_trigger_tags(span, original_event, original_context):
        try:
            lambda_event_type = lambda_event_utils.get_lambda_event_type(original_event, original_context)

            if lambda_event_type == lambda_event_utils.LambdaEventType.Kinesis:
                lambda_event_utils.inject_trigger_tags_for_kinesis(span, original_event)
            elif lambda_event_type == lambda_event_utils.LambdaEventType.Firehose:
                lambda_event_utils.inject_trigger_tags_for_firehose(span, original_event)
            elif lambda_event_type == lambda_event_utils.LambdaEventType.DynamoDB:
                lambda_event_utils.inject_trigger_tags_for_dynamodb(span, original_event)
            elif lambda_event_type == lambda_event_utils.LambdaEventType.SNS:
                lambda_event_utils.inject_trigger_tags_for_sns(span, original_event)
            elif lambda_event_type == lambda_event_utils.LambdaEventType.SQS:
                lambda_event_utils.inject_trigger_tags_for_sqs(span, original_event)
            elif lambda_event_type == lambda_event_utils.LambdaEventType.S3:
                lambda_event_utils.inject_trigger_tags_for_s3(span, original_event)
            elif lambda_event_type == lambda_event_utils.LambdaEventType.CloudWatchSchedule:
                lambda_event_utils.inject_trigger_tags_for_cloudwatch_schedule(span, original_event)
            elif lambda_event_type == lambda_event_utils.LambdaEventType.CloudWatchLogs:
                lambda_event_utils.inject_trigger_tags_for_cloudwatch_logs(span, original_event)
            elif lambda_event_type == lambda_event_utils.LambdaEventType.CloudFront:
                lambda_event_utils.inject_trigger_tags_for_cloudfront(span, original_event)
            elif lambda_event_type == lambda_event_utils.LambdaEventType.APIGatewayProxy:
                lambda_event_utils.inject_trigger_tags_for_api_gateway_proxy(span, original_event)
            elif lambda_event_type == lambda_event_utils.LambdaEventType.APIGateway:
                lambda_event_utils.inject_trigger_tags_for_api_gateway(span, original_event)
            elif lambda_event_type == lambda_event_utils.LambdaEventType.Lambda:
                lambda_event_utils.inject_trigger_tags_for_lambda(span, original_context)
        except Exception as e:
            debug_logger("Cannot inject trigger tags. " + str(e))
