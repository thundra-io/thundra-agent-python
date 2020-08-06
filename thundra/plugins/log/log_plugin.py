import logging
import sys
import uuid

import wrapt

from thundra import constants
from thundra.application.application_manager import ApplicationManager
from thundra.compat import PY37
from thundra.config import config_names
from thundra.config.config_provider import ConfigProvider
from thundra.context.execution_context_manager import ExecutionContextManager
from thundra.plugins.log import log_support
from thundra.plugins.log.thundra_log_handler import ThundraLogHandler
from thundra.plugins.log.thundra_logger import StreamToLogger

logger = logging.getLogger(__name__)


class LogPlugin:

    def __init__(self, plugin_context=None):
        self.hooks = {
            'before:invocation': self.before_invocation,
            'after:invocation': self.after_invocation
        }
        self.old_stdout = sys.stdout
        self.plugin_context = plugin_context
        if not ConfigProvider.get(config_names.THUNDRA_LOG_CONSOLE_DISABLE):
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

    def before_invocation(self, execution_context):
        self.old_stdout = sys.stdout
        if (not ConfigProvider.get(config_names.THUNDRA_LOG_CONSOLE_DISABLE)) and (not PY37):
            sys.stdout = StreamToLogger(self.logger, self.old_stdout)
        if not execution_context.transaction_id:
            execution_context.transaction_id = str(uuid.uuid4())

    def after_invocation(self, execution_context):
        if (not ConfigProvider.get(config_names.THUNDRA_LOG_CONSOLE_DISABLE)) and (not PY37):
            sys.stdout = self.old_stdout
        log_data = {
            'type': "Log",
            'agentVersion': constants.THUNDRA_AGENT_VERSION,
            'dataModelVersion': constants.DATA_FORMAT_VERSION,
            'traceId': execution_context.trace_id,
            'transactionId': execution_context.transaction_id,
        }

        for log in execution_context.logs:
            # Add application related data
            application_info = ApplicationManager.get_application_info()
            log_data.update(application_info)
            log.update(log_data)
            if self.check_sampled(log):
                log_report = {
                    'data': log,
                    'type': 'Log',
                    'apiKey': self.plugin_context.api_key,
                    'dataModelVersion': constants.DATA_FORMAT_VERSION
                }
                execution_context.report(log_report)

    def check_sampled(self, log):
        sampler = log_support.get_sampler()
        sampled = True
        if sampler is not None:
            try:
                sampled = sampler.is_sampled(log)
            except Exception:
                pass
        return sampled
