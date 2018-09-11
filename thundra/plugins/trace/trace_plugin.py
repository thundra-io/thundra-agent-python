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
            'type': "Trace",
            'agentVersion': '',
            'dataModelVersion': constants.DATA_FORMAT_VERSION,
            'applicationId': utils.get_application_id(context),
            'applicationDomainName':'',
            'applicationClassName': 'ExecutionContext',
            'applicationName': function_name,
            'applicationStage': '',
            'applicationRuntime': 'python',
            'applicationRuntimeVersion': getattr(context, constants.CONTEXT_FUNCTION_VERSION, None),
            'applicationTags': {},

            'rootSpanId': None,
            'startTimestamp': self.start_time,
            'endTimestamp': None,
            'duration': None,
            'tags': {},
        }
        self.scope = self.tracer.start_active_span(operation_name=function_name,
                                                   start_time=self.start_time,
                                                   finish_on_close=True)


        TracePlugin.IS_COLD_START = False

    def after_invocation(self, data):
        self.end_time = int(time.time() * 1000)
        self.scope.close()
        if self.scope.span is not None and self.scope.span.duration != -1:
            self.end_time = self.scope.span.start_time + self.scope.span.duration

        duration = self.end_time - self.start_time

        self.trace_data['root_span'] = self.scope
        self.trace_data['duration'] = duration
        self.trace_data['startTimestamp'] = self.start_time
        self.trace_data['endTimestamp'] = self.end_time

        span_stack = self.tracer.recorder.active_span_stack if self.tracer is not None else None
        for span in span_stack:
            current_span = self.build_span(span)
            self.span_data_list.append(current_span)


        reporter = data['reporter']
        report_data = {
            'apiKey': reporter.api_key,
            'type': 'Trace',
            'dataModelVersion': constants.DATA_FORMAT_VERSION,
            'data': self.trace_data
        }
        reporter.add_report(report_data)
        reporter.add_report(self.span_data_list)

    def build_span(self, span):
        close_time = span.key.start_time + span.key.duration
        span_data = {
            'contextName': span.operation_name,
            'id': span.span_id,
            'openTimestamp': int(span.key.start_time),
            'closeTimestamp': int(close_time),
            'props': span.tags,
            'children': []
        }
        return span_data
