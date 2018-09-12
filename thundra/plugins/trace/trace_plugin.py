import time
import uuid

import thundra.utils as utils
from thundra import constants
from thundra.opentracing.tracer import ThundraTracer


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
            'type': "Log",
            'agentVersion': '',
            'dataModelVersion': constants.DATA_FORMAT_VERSION,
            'applicationId': utils.get_application_id(context),
            'applicationDomainName': 'root_{}'.format(str(uuid.uuid4())),
            'applicationClassName': 'root_{}'.format(str(uuid.uuid4())),
            'applicationName': function_name,
            'applicationVersion': getattr(context, constants.CONTEXT_FUNCTION_VERSION, None),
            'applicationStage':'',
            'applicationRuntime':'python',
            'applicationRuntimeVersion':'',
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


        TracePlugin.IS_COLD_START = False

    def after_invocation(self, data):
        self.end_time = int(time.time() * 1000)
        root_span = self.tracer.recorder.get_root_span()
        reporter = data['reporter']
        span_stack = self.tracer.recorder.active_span_stack if self.tracer is not None else None
        for span in span_stack:
            current_span_data = self.wrap_span(self.build_span(span, data), reporter.api_key)
            self.span_data_list.append(current_span_data)

        self.scope.close()
        if self.scope.span is not None and self.scope.span.duration != -1:
            self.end_time = self.scope.span.start_time + self.scope.span.duration

        duration = self.end_time - self.start_time

        self.trace_data['rootSpanId'] = root_span.span_id
        self.trace_data['applicationDomainName'] = root_span.domain_name if root_span is not None \
                                        else self.trace_data['applicationDomainName']
        self.trace_data['applicationClassName'] = root_span.class_name if root_span is not None \
                                                        else self.trace_data['applicationClassName']
        self.trace_data['duration'] = duration
        self.trace_data['startTimestamp'] = self.start_time
        self.trace_data['endTimestamp'] = self.end_time






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
            'id': str(uuid.uuid4()),
            'type': "Span",
            'agentVersion': '',
            'dataModelVersion': constants.DATA_FORMAT_VERSION,
            'applicationId': utils.get_application_id(context),
            'applicationDomainName': span.domain_name,
            'applicationClassName': span.class_name,
            'applicationName': function_name,
            'applicationStage': '',
            'applicationRuntime': 'python',
            'applicationRuntimeVersion': getattr(context, constants.CONTEXT_FUNCTION_VERSION, None),
            'applicationTags': {},

            'traceId': span.trace_id,
            'transactionID': data['transactionId'],
            'parentSpanId': span.context.parent_span_id,
            'spanOrder': -1,
            'domainName': span.domain_name,
            'className': span.class_name,
            'serviceName': '',
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