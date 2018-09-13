import time
import uuid

import thundra.utils as utils
from thundra import constants
from thundra.opentracing.tracer import ThundraTracer
import sys


class TracePlugin:
    IS_COLD_START = True

    def __init__(self):
        self.hooks = {
            'before:invocation': self.before_invocation,
            'after:invocation': self.after_invocation
        }
        self.tracer = ThundraTracer.getInstance()
        self.scope = None
        self.start_time = 0
        self.end_time = 0
        self.trace_data = {}
        self.span_data_list = []
        self.root_span = None

    def before_invocation(self, data):

        if constants.REQUEST_COUNT > 0:
            TracePlugin.IS_COLD_START = False
        context = data['context']

        context_id = str(uuid.uuid4())
        data['contextId'] = context_id
        function_name = getattr(context, constants.CONTEXT_FUNCTION_NAME, None)

        self.start_time = int(time.time() * 1000)
        self.trace_data = {
            'id': str(uuid.uuid4()),
            'type': "Trace",
            'agentVersion': '',
            'dataModelVersion': constants.DATA_FORMAT_VERSION,
            'applicationId': utils.get_application_id(context),
            'applicationDomainName': '',
            'applicationClassName': '',
            'applicationName': function_name,
            'applicationVersion': getattr(context, constants.CONTEXT_FUNCTION_VERSION, None),
            'applicationStage':'',
            'applicationRuntime':'python',
            'applicationRuntimeVersion': sys.version_info[0],
            'applicationTags': {},

            'rootSpanId': None,
            'startTimestamp': self.start_time,
            'finishTimestamp': None,
            'duration': None,
            'tags': {},
        }
        self.scope = self.tracer.start_active_span(operation_name=function_name,
                                                   start_time=self.start_time,
                                                   finish_on_close=True)
        self.root_span = self.tracer.recorder.get_active_span()

        TracePlugin.IS_COLD_START = False

    def after_invocation(self, data):
        self.end_time = int(time.time() * 1000)
        self.scope.close()
        if self.scope.span is not None and self.scope.span.duration != -1:
            self.end_time = self.scope.span.start_time + self.scope.span.duration

        duration = self.end_time - self.start_time

        root_span = self.root_span
        reporter = data['reporter']
        span_stack = self.tracer.recorder.finished_span_stack if self.tracer is not None else None
        for span in span_stack:
            current_span_data = self.wrap_span(self.build_span(span, data), reporter.api_key)
            self.span_data_list.append(current_span_data)

        self.trace_data['rootSpanId'] = root_span.span_id
        self.trace_data['applicationDomainName'] = root_span.domain_name or ''
        self.trace_data['applicationClassName'] = root_span.class_name or ''
        self.trace_data['duration'] = duration
        self.trace_data['startTimestamp'] = self.start_time
        self.trace_data['finishTimestamp'] = self.end_time

        report_data = {
            'apiKey': reporter.api_key,
            'type': 'Trace',
            'dataModelVersion': constants.DATA_FORMAT_VERSION,
            'data': self.trace_data
        }
        reporter.add_report(report_data)
        reporter.add_report(self.span_data_list)

    def build_span(self, span, data):
        close_time = span.start_time + span.duration
        context = data['context']
        function_name = getattr(context, constants.CONTEXT_FUNCTION_NAME, None)

        span_data = {
            'id': span.context.span_id,
            'type': "Span",
            'agentVersion': '',
            'dataModelVersion': constants.DATA_FORMAT_VERSION,
            'applicationId': utils.get_application_id(context),
            'applicationDomainName': span.domain_name or '',
            'applicationClassName': span.class_name or '',
            'applicationName': function_name,
            'applicationVersion': getattr(context, constants.CONTEXT_FUNCTION_VERSION, None),
            'applicationStage': '',
            'applicationRuntime': 'python',
            'applicationRuntimeVersion': sys.version_info[0],
            'applicationTags': {},

            'traceId': span.trace_id,
            'transactionId': data['transactionId'],
            'parentSpanId': span.context.parent_span_id or '',
            'spanOrder': -1,
            'domainName': span.domain_name or '',
            'className': span.class_name or '',
            'serviceName': '',
            'operationName': span.operation_name,
            'startTimestamp': span.start_time,
            'finishTimestamp': close_time,
            'duration': span.duration,
            'tags':{}
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