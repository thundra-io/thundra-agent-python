import logging
import traceback
import uuid

from thundra import constants
from thundra.opentracing.tracer import ThundraTracer
from thundra.plugins.config.trace_config import TraceConfig
from thundra.plugins.invocation import invocation_support
from thundra.plugins.trace import trace_support

logger = logging.getLogger(__name__)


class TracePlugin:

    def __init__(self, plugin_context, config=None):
        self.hooks = {
            'before:invocation': self.before_invocation,
            'after:invocation': self.after_invocation
        }
        self.tracer = ThundraTracer.get_instance()
        self.plugin_context = plugin_context
        if isinstance(config, TraceConfig):
            self.config = config
        else:
            self.config = TraceConfig()

    def before_invocation(self, execution_context):
        executor = self.plugin_context.executor
        if executor:
            executor.start_trace(self.plugin_context, execution_context, self.tracer)

    def after_invocation(self, execution_context):
        executor = self.plugin_context.executor
        if executor:
            executor.finish_trace(execution_context)

        span_stack = execution_context.recorder.get_spans()

        sampled = True
        if len(span_stack) > 0:
            sampled = self.check_sampled(span_stack[0])

        span_data_list = []
        for span in span_stack:
            if sampled:
                current_span_data = self.wrap_span(self.build_span(span, execution_context),
                                                   self.plugin_context.api_key)
                span_data_list.append(current_span_data)

        execution_context.recorder.clear()

        if execution_context.error:
            error = execution_context.error
            self.set_error_to_root_span(execution_context.root_span, error)
        elif execution_context.user_error:
            self.set_error_to_root_span(execution_context.root_span, execution_context.user_error)

        execution_context.report(span_data_list)

        invocation_support.clear_error()

    @staticmethod
    def set_error_to_root_span(root_span, error):
        root_span.set_tag('error', True)
        if isinstance(error, Exception):
            error_type = type(error)
            root_span.set_tag('error.kind', error_type.__name__)
            root_span.set_tag('error.message', str(error))

            if hasattr(error, 'code'):
                root_span.set_tag('error.code', error.code)
            if hasattr(error, '__traceback__'):
                root_span.set_tag('error.stack', ''.join(
                    traceback.format_exception(error_type, error, error.__traceback__)))

        elif isinstance(error, dict):
            root_span.set_tag('error.kind', error.get('type'))
            root_span.set_tag('error.message', error.get('message'))
            if error.get('traceback'):
                root_span.set_tag('error.stack', error.get('traceback'))

    def build_span(self, span, execution_context):
        if not execution_context.transaction_id:
            execution_context.transaction_id = str(uuid.uuid4())

        span_data = {
            'id': span.context.span_id,
            'type': "Span",
            'agentVersion': constants.THUNDRA_AGENT_VERSION,
            'dataModelVersion': constants.DATA_FORMAT_VERSION,
            'traceId': span.context.trace_id,
            'transactionId': execution_context.transaction_id,
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
        application_info = self.plugin_context.application_info
        span_data.update(application_info)

        return span_data

    @staticmethod
    def wrap_span(span_data, api_key):
        report_data = {
            'apiKey': api_key,
            'type': 'Span',
            'dataModelVersion': constants.DATA_FORMAT_VERSION,
            'data': span_data
        }

        return report_data

    def check_sampled(self, span):
        sampler = trace_support.get_sampler()
        if self.config.sampler:
            sampler = self.config.sampler

        sampled = True
        if sampler is not None:
            try:
                sampled = sampler.is_sampled(span)
            except Exception as e:
                logger.error("error while sampling spans: %s", e)
        return sampled
