import wrapt
import logging
import uuid
import sys

from thundra.opentracing.tracer import ThundraTracer
from thundra.plugins.log.thundra_log_handler import logs
from thundra import utils, constants, config, application_support
from thundra.plugins.log.thundra_log_handler import ThundraLogHandler
from thundra.plugins.log.thundra_logger import StreamToLogger
from thundra.plugins.log import log_support
from thundra.compat import PY37

logger = logging.getLogger(__name__)


class LogPlugin:

    def __init__(self):
        self.hooks = {
            'before:invocation': self.before_invocation,
            'after:invocation': self.after_invocation
        }
        self.log_data = {}
        self.tracer = ThundraTracer.get_instance()
        self.old_stdout = sys.stdout
        if not config.disable_stdout_logs():
            self.logger = logging.getLogger('STDOUT')
            self.handler = ThundraLogHandler()
            self.logger.addHandler(self.handler)
            self.logger.setLevel(logging.INFO)
            self.handler.setLevel(logging.INFO)
            self.logger.propagate = False
            if PY37:
                wrapt.wrap_function_wrapper(
                    'builtins',
                    'print',
                    self._wrapper
                )

    def _wrapper(self, wrapped, instance, args, kwargs):
        try:
            wrapped(*args, **kwargs)
            self.logger.info(str(args[0]))
        except:
            pass

    def before_invocation(self, plugin_context):
        del logs[:]
        self.old_stdout = sys.stdout
        if (not config.disable_stdout_logs()) and (not PY37):
            sys.stdout = StreamToLogger(self.logger, self.old_stdout)
        context = plugin_context['context']
        plugin_context['transaction_id'] = plugin_context.get('transaction_id', str(uuid.uuid4()))
        self.log_data = {
            'type': "Log",
            'agentVersion': constants.THUNDRA_AGENT_VERSION,
            'dataModelVersion': constants.DATA_FORMAT_VERSION,
            'traceId': plugin_context.get('trace_id', ""),
            'transactionId': plugin_context.get('transaction_id'),
        }
        # Add application related data
        application_info = application_support.get_application_info()
        self.log_data.update(application_info)

    def after_invocation(self, plugin_context):
        if (not config.disable_stdout_logs()) and (not PY37):
            sys.stdout = self.old_stdout
        context = plugin_context['context']

        reporter = plugin_context['reporter']
        for log in logs:
            log.update(self.log_data)
            if self.check_sampled(log):
                log_report = {
                    'data': log,
                    'type': 'Log',
                    'apiKey': reporter.api_key,
                    'dataModelVersion': constants.DATA_FORMAT_VERSION
                }
                reporter.add_report(log_report)
        del logs[:]

    def check_sampled(self, log):
        sampler = log_support.get_sampler()
        sampled = True
        if sampler is not None:
            try:
                sampled = sampler.is_sampled(log)
            except Exception as e:
                pass
        return sampled