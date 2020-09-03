import logging
import sys
from threading import Lock

import wrapt

from thundra import constants
from thundra.compat import PY37, PY38
from thundra.config import config_names
from thundra.config.config_provider import ConfigProvider
from thundra.plugins.config.log_config import LogConfig
from thundra.plugins.log import log_support
from thundra.plugins.log.thundra_log_handler import ThundraLogHandler
from thundra.plugins.log.thundra_logger import StreamToLogger


class LogPlugin:
    lock = Lock()
    wrapped = False

    def __init__(self, plugin_context=None, config=None):
        self.hooks = {
            'before:invocation': self.before_invocation,
            'after:invocation': self.after_invocation
        }
        self.plugin_context = plugin_context
        self.logger = logging.getLogger('STDOUT')

        if isinstance(config, LogConfig):
            self.config = config
        else:
            self.config = LogConfig()

        with LogPlugin.lock:
            if (not LogPlugin.wrapped) and (
                    not ConfigProvider.get(config_names.THUNDRA_LOG_CONSOLE_DISABLE, not self.config.enabled)):
                if PY37 or PY38:
                    wrapt.wrap_function_wrapper(
                        'builtins',
                        'print',
                        self._wrapper
                    )
                else:
                    sys.stdout = StreamToLogger(self.logger, sys.stdout)
                LogPlugin.wrapped = True

        if not ConfigProvider.get(config_names.THUNDRA_LOG_CONSOLE_DISABLE, not self.config.enabled):
            handler = ThundraLogHandler()
            has_thundra_log_handler = False
            for log_handlers in self.logger.handlers:
                if isinstance(log_handlers, ThundraLogHandler):
                    has_thundra_log_handler = True
            if not has_thundra_log_handler:
                self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
            handler.setLevel(logging.INFO)
            self.logger.propagate = False

    def _wrapper(self, wrapped, instance, args, kwargs):
        try:
            wrapped(*args, **kwargs)
            self.logger.info(str(args[0]))
        except:
            pass

    def before_invocation(self, execution_context):
        execution_context.capture_log = True

    def after_invocation(self, execution_context):
        execution_context.capture_log = False
        log_data = {
            'type': "Log",
            'agentVersion': constants.THUNDRA_AGENT_VERSION,
            'dataModelVersion': constants.DATA_FORMAT_VERSION,
            'traceId': execution_context.trace_id,
            'transactionId': execution_context.transaction_id,
        }

        for log in execution_context.logs:
            # Add application related data
            application_info = self.plugin_context.application_info
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
        if self.config.sampler:
            sampler = self.config.sampler
        sampled = True
        if sampler is not None:
            try:
                sampled = sampler.is_sampled(log)
            except Exception:
                pass
        return sampled
