import time
import uuid

from thundra.opentracing.tracer import ThundraTracer
from thundra.plugins.invocation import invocation_support
from thundra.plugins.log.thundra_logger import debug_logger
from thundra import utils, constants, application_support, lambda_event_utils, config


class TracePlugin:

    def __init__(self):
        self.hooks = {
            'before:invocation': self.before_invocation,
            'after:invocation': self.after_invocation
        }
        self.tracer = ThundraTracer.get_instance()
        self.start_time = 0
        self.end_time = 0
        self.trace_data = {}
        self.scope = None
        self.root_span = None
        self.span_data_list = []

    def before_invocation(self, plugin_context):
        self.set_start_time(plugin_context)

        context = plugin_context['context']
        trace_id = str(uuid.uuid4())
        transaction_id = plugin_context.get('transaction_id', str(uuid.uuid4()))
        plugin_context['transaction_id'] = transaction_id
        plugin_context['trace_id'] = trace_id
        self.trace_data = {
            'id': trace_id,
            'type': "Trace",
            'agentVersion': constants.THUNDRA_AGENT_VERSION,
            'dataModelVersion': constants.DATA_FORMAT_VERSION,
            'rootSpanId': None,
            'startTimestamp': self.start_time,
            'finishTimestamp': None,
            'duration': None,
            'tags': {},
        }
        # Add application related data
        application_info = application_support.get_application_info()
        self.trace_data.update(application_info)
        # Start root span
        self.scope = self.tracer.start_active_span(operation_name=invocation_support.function_name,
                                                   start_time=self.start_time,
                                                   finish_on_close=False,
                                                   trace_id=trace_id,
                                                   transaction_id=transaction_id)
        self.root_span = self.scope.span

        # Set root span class and domain names
        self.root_span.class_name = constants.ClassNames['LAMBDA']
        self.root_span.domain_name = constants.DomainNames['API']
        # Add root span tags
        plugin_context['span_id'] = self.root_span.context.span_id
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
        
        self.root_span.on_started()

    def set_start_time(self, plugin_context):
        if 'start_time' in plugin_context:
            self.start_time = plugin_context['start_time']
        else:
            self.start_time = int(time.time() * 1000)
            plugin_context['start_time'] = self.start_time

    def set_end_time(self, plugin_context):
        if 'end_time' in plugin_context:
            self.end_time = plugin_context['end_time']
        else:
            self.end_time = int(time.time() * 1000)
            plugin_context['end_time'] = self.end_time

    def after_invocation(self, plugin_context):
        self.set_end_time(plugin_context)

        try:
            self.root_span.finish(f_time=self.end_time)
        except Exception as injected_err:
            # TODO: handle root span finish errors
            pass
        finally:
            self.scope.close()

        context = plugin_context['context']
        reporter = plugin_context['reporter']

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

        duration = self.end_time - self.start_time

        span_stack = self.tracer.get_spans()

        for span in span_stack:
            current_span_data = self.wrap_span(self.build_span(span, plugin_context), reporter.api_key)
            self.span_data_list.append(current_span_data)

        self.tracer.clear()
        self.trace_data['rootSpanId'] = self.root_span.context.span_id
        self.trace_data['duration'] = duration
        self.trace_data['startTimestamp'] = self.start_time
        self.trace_data['finishTimestamp'] = self.end_time

        if 'error' in plugin_context:
            error = plugin_context['error']
            error_type = type(error)
            # Adding tags
            self.root_span.set_tag('error', True)
            self.root_span.set_tag('error.kind', error_type.__name__)
            self.root_span.set_tag('error.message', str(error))
            if hasattr(error, 'code'):
                self.root_span.set_tag('error.code', error.code)
            if hasattr(error, 'object'):
                self.root_span.set_tag('error.object', error.object)
            if hasattr(error, 'stack'):
                self.root_span.set_tag('error.stack', error.stack)

        report_data = {
            'apiKey': reporter.api_key,
            'type': 'Trace',
            'dataModelVersion': constants.DATA_FORMAT_VERSION,
            'data': self.trace_data
        }

        reporter.add_report(report_data)
        reporter.add_report(self.span_data_list)

        self.tracer.clear()
        self.flush_current_span_data()

    def flush_current_span_data(self):
        self.span_data_list.clear()

    def build_span(self, span, plugin_context):
        context = plugin_context['context']
        transaction_id = plugin_context['transaction_id'] or str(uuid.uuid4())

        span_data = {
            'id': span.context.span_id,
            'type': "Span",
            'agentVersion': constants.THUNDRA_AGENT_VERSION,
            'dataModelVersion': constants.DATA_FORMAT_VERSION,
            'traceId': span.context.trace_id,
            'transactionId': transaction_id,
            'parentSpanId': span.context.parent_span_id or '',
            'spanOrder': span.span_order,
            'domainName': span.domain_name or '',
            'className': span.class_name or '',
            'serviceName': '',
            'operationName': span.operation_name,
            'startTimestamp': span.start_time,
            'finishTimestamp': span.finish_time,
            'duration': span.get_duration(),
            'logs': span.logs,
            'tags': span.tags
        }

        # Add application related data
        application_info = application_support.get_application_info()
        span_data.update(application_info)

        return span_data

    def wrap_span(self, span_data, api_key):
        report_data = {
            'apiKey': api_key,
            'type': 'Span',
            'dataModelVersion': constants.DATA_FORMAT_VERSION,
            'data': span_data
        }

        return report_data

    def _inject_trigger_tags(self, span, original_event, original_context):
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
