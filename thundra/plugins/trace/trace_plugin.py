import time
import uuid

import thundra.utils as utils
from thundra import constants
from thundra.opentracing.tracer import ThundraTracer
import sys


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
        context = plugin_context['context']
        trace_id = str(uuid.uuid4())
        transaction_id = context.aws_request_id
        function_name = getattr(context, constants.CONTEXT_FUNCTION_NAME, None)

        self.start_time = int(time.time() * 1000)

        plugin_context['transaction_id'] = transaction_id
        plugin_context['trace_id'] = trace_id

        self.trace_data = {
            'id': trace_id,
            'type': "Trace",
            'agentVersion': constants.THUNDRA_AGENT_VERSION,
            'dataModelVersion': constants.DATA_FORMAT_VERSION,
            'applicationId': utils.get_application_id(context),
            'applicationDomainName': constants.AWS_LAMBDA_APPLICATION_DOMAIN_NAME,
            'applicationClassName': constants.AWS_LAMBDA_APPLICATION_CLASS_NAME,
            'applicationName': function_name,
            'applicationVersion': getattr(context, constants.CONTEXT_FUNCTION_VERSION, None),
            'applicationStage': utils.get_configuration(constants.THUNDRA_APPLICATION_STAGE, ''),
            'applicationRuntime': 'python',
            'applicationRuntimeVersion': str(sys.version_info[0]),
            'applicationTags': {},

            'rootSpanId': None,
            'startTimestamp': self.start_time,
            'finishTimestamp': None,
            'duration': None,
            'tags': {},
        }
        self.scope = self.tracer.start_active_span(operation_name=function_name,
                                                   start_time=self.start_time,
                                                   finish_on_close=True,
                                                   trace_id=trace_id,
                                                   transaction_id=transaction_id)
        self.root_span = self.scope.span
        plugin_context['span_id'] = self.root_span.context.trace_id

    def after_invocation(self, plugin_context):
        self.scope.close()

        self.end_time = int(time.time() * 1000)

        context = plugin_context['context']
        reporter = plugin_context['reporter']

        #### ADDING TAGS ####
        self.root_span.set_tag('aws.region', utils.get_aws_region_from_arn(getattr(context, constants.CONTEXT_INVOKED_FUNCTION_ARN, None)))
        self.root_span.set_tag('aws.lambda.name', getattr(context, constants.CONTEXT_FUNCTION_NAME, None))
        self.root_span.set_tag('aws.lambda.arn', getattr(context, constants.CONTEXT_INVOKED_FUNCTION_ARN, None))
        self.root_span.set_tag('aws.lambda.memory.limit', getattr(context, constants.CONTEXT_MEMORY_LIMIT_IN_MB, None))
        self.root_span.set_tag('aws.lambda.log_group_name', getattr(context, constants.CONTEXT_LOG_GROUP_NAME, None))
        self.root_span.set_tag('aws.lambda.log_stream_name', getattr(context, constants.CONTEXT_LOG_STREAM_NAME, None))
        skip_request = utils.get_configuration(constants.THUNDRA_LAMBDA_TRACE_REQUEST_SKIP)
        skip_response = utils.get_configuration(constants.THUNDRA_LAMBDA_TRACE_RESPONSE_SKIP)
        if skip_request != True:
            self.root_span.set_tag('aws.lambda.invocation.request', plugin_context.get('request', None))
        if skip_response != True:
            self.root_span.set_tag('aws.lambda.invocation.response', plugin_context.get('response', None))

        if self.root_span is not None and self.root_span.duration != -1:
            self.end_time = self.root_span.start_time + self.root_span.duration

        duration = self.end_time - self.start_time

        span_stack = self.tracer.get_finished_stack() if self.tracer is not None else None
        for span in span_stack:
            current_span_data = self.wrap_span(self.build_span(span, plugin_context), reporter.api_key)
            self.span_data_list.append(current_span_data)
        self.tracer.clear()

        self.trace_data['rootSpanId'] = self.root_span.context.span_id
        self.trace_data['duration'] = duration
        self.trace_data['startTimestamp'] = self.start_time
        self.trace_data['finishTimestamp'] = self.end_time

        #### ADDING TAGS ####
        self.trace_data['tags']['aws.region'] = utils.get_aws_region_from_arn(getattr(context, constants.CONTEXT_INVOKED_FUNCTION_ARN, None))
        self.trace_data['tags']['aws.lambda.name'] = getattr(context, constants.CONTEXT_FUNCTION_NAME, None)
        self.trace_data['tags']['aws.lambda.arn'] = getattr(context, constants.CONTEXT_INVOKED_FUNCTION_ARN, None)
        self.trace_data['tags']['aws.lambda.memory.limit'] = getattr(context, constants.CONTEXT_MEMORY_LIMIT_IN_MB, None)
        self.trace_data['tags']['aws.lambda.log_group_name'] = getattr(context, constants.CONTEXT_LOG_GROUP_NAME, None)
        self.trace_data['tags']['aws.lambda.log_stream_name'] = getattr(context, constants.CONTEXT_LOG_STREAM_NAME, None)

        if 'error' in plugin_context:
            error = plugin_context['error']
            error_type = type(error)
            # Adding tags
            self.trace_data['tags']['error'] = True
            self.root_span.set_tag('error', True)
            self.trace_data['tags']['error.kind'] = error_type.__name__
            self.root_span.set_tag('error.kind', error_type.__name__)
            self.trace_data['tags']['error.message'] = str(error)
            self.root_span.set_tag('error.message', str(error))
            if hasattr(error, 'code'):
                self.trace_data['tags']['error.code'] = error.code
                self.root_span.set_tag('error.code', error.code)
            if hasattr(error, 'object'):
                self.trace_data['tags']['error.object'] = error.object
                self.root_span.set_tag('error.object', error.object)
            if hasattr(error, 'stack'):
                self.trace_data['tags']['error.stack'] = error.stack
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
        close_time = span.start_time + span.duration
        context = plugin_context['context']
        transaction_id = plugin_context['transaction_id'] or plugin_context['context'].aws_request_id
        function_name = getattr(context, constants.CONTEXT_FUNCTION_NAME, None)

        span_data = {
            'id': span.context.span_id,
            'type': "Span",
            'agentVersion': constants.THUNDRA_AGENT_VERSION,
            'dataModelVersion': constants.DATA_FORMAT_VERSION,
            'applicationId': utils.get_application_id(context),
            'applicationDomainName': constants.AWS_LAMBDA_APPLICATION_DOMAIN_NAME,
            'applicationClassName': constants.AWS_LAMBDA_APPLICATION_CLASS_NAME,
            'applicationName': function_name,
            'applicationVersion': getattr(context, constants.CONTEXT_FUNCTION_VERSION, None),
            'applicationStage': utils.get_configuration(constants.THUNDRA_APPLICATION_STAGE, ''),
            'applicationRuntime': 'python',
            'applicationRuntimeVersion': str(sys.version_info[0]),
            'applicationTags': {},

            'traceId': span.context.trace_id,
            'transactionId': transaction_id,
            'parentSpanId': span.context.parent_span_id or '',
            'spanOrder': -1,
            'domainName': span.domain_name or '',
            'className': span.class_name or '',
            'serviceName': '',
            'operationName': span.operation_name,
            'startTimestamp': span.start_time,
            'finishTimestamp': close_time,
            'duration': span.duration,
            'logs': span.logs,
            'tags': span.tags
        }

        return span_data

    def wrap_span(self, span_data, api_key):
        report_data = {
            'apiKey': api_key,
            'type': 'Span',
            'dataModelVersion': constants.DATA_FORMAT_VERSION,
            'data': span_data
        }

        return report_data
