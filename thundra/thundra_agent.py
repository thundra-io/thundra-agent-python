import signal
import threading
from functools import wraps
import time
import logging

from thundra import constants
from thundra.plugins.invocation.invocation_plugin import InvocationPlugin
from thundra.plugins.log.log_plugin import LogPlugin
from thundra.plugins.metric.metric_plugin import MetricPlugin
from thundra.plugins.trace.trace_plugin import TracePlugin
from thundra.plugins.trace.patcher import ImportPatcher
from thundra.plugins.aws_xray.xray_plugin import AWSXRayPlugin
from thundra.reporter import Reporter

import thundra.utils as utils
import thundra.application_support as application_support 

logger = logging.getLogger(__name__)

class Thundra:

    def __init__(self,
                 api_key=None,
                 disable_trace=False,
                 disable_metric=False,
                 disable_log=False):

        constants.REQUEST_COUNT = 0

        self.plugins = []
        api_key_from_environment_variable = utils.get_configuration(constants.THUNDRA_APIKEY)
        self.api_key = api_key_from_environment_variable if api_key_from_environment_variable is not None else api_key
        if self.api_key is None:
            logger.error('Please set "thundra_apiKey" from environment variables in order to use Thundra')

        disable_trace_by_env = utils.get_configuration(constants.THUNDRA_DISABLE_TRACE)
        if not utils.should_disable(disable_trace_by_env, disable_trace):
            self.plugins.append(TracePlugin())

        self.plugins.append(InvocationPlugin())
        self.plugin_context = {}

        disable_metric_by_env = utils.get_configuration(constants.THUNDRA_DISABLE_METRIC)
        if not utils.should_disable(disable_metric_by_env, disable_metric):
            self.plugins.append(MetricPlugin())

        disable_log_by_env = utils.get_configuration(constants.THUNDRA_DISABLE_LOG)
        if not utils.should_disable(disable_log_by_env, disable_log):
            self.plugins.append(LogPlugin())

        thundra_lambda_trace_instrument_disable = utils.get_configuration(
            constants.THUNDRA_LAMBDA_TRACE_INSTRUMENT_DISABLE)
        self.trace_instrument_disable = utils.should_disable(thundra_lambda_trace_instrument_disable, False)

        timeout_margin = utils.get_configuration(constants.THUNDRA_LAMBDA_TIMEOUT_MARGIN)
        self.timeout_margin = int(timeout_margin) if timeout_margin is not None else 0
        if self.timeout_margin <= 0:
            self.timeout_margin = constants.DEFAULT_LAMBDA_TIMEOUT_MARGIN

        enable_xray_trace_by_env = utils.get_configuration(constants.THUNDRA_LAMBDA_TRACE_ENABLE_XRAY)
        if utils.should_disable(enable_xray_trace_by_env):
            self.plugins.append(AWSXRayPlugin())

        self.reporter = Reporter(self.api_key)

        if not self.trace_instrument_disable:
            self.import_patcher = ImportPatcher()

    def __call__(self, original_func):
        is_thundra_disabled_by_env = utils.get_configuration(constants.THUNDRA_DISABLE)
        should_disable_thundra = utils.should_disable(is_thundra_disabled_by_env)
        if should_disable_thundra:
            return original_func

        self.plugin_context['reporter'] = self.reporter

        @wraps(original_func)
        def wrapper(event, context):
            if self.check_and_handle_warmup_request(event):
                return None

            constants.REQUEST_COUNT += 1

            self.plugin_context['request'] = event
            self.plugin_context['context'] = context
            application_support.clear_application_tags()
            self.execute_hook('before:invocation', self.plugin_context)
            if threading.current_thread().__class__.__name__ == '_MainThread':
                signal.signal(signal.SIGALRM, self.timeout_handler)
                if hasattr(context, 'get_remaining_time_in_millis'):
                    timeout_duration = context.get_remaining_time_in_millis() - self.timeout_margin
                    if timeout_duration <= 0:
                        timeout_duration = context.get_remaining_time_in_millis() - \
                                                    constants.DEFAULT_LAMBDA_TIMEOUT_MARGIN
                        logger.warning('Given timeout margin is bigger than lambda timeout duration and '
                                       'since the difference is negative, it is set to default value (' +
                                       str(constants.DEFAULT_LAMBDA_TIMEOUT_MARGIN) + ')')
                    signal.setitimer(signal.ITIMER_REAL, timeout_duration / 1000.0)
            try:
                response = original_func(event, context)
                self.plugin_context['response'] = response
            except Exception as e:
                self.plugin_context['error'] = e
                self.prepare_and_send_reports()
                raise e
            finally:
                if threading.current_thread().__class__.__name__ == '_MainThread':
                    signal.setitimer(signal.ITIMER_REAL, 0)
            application_support.parse_application_tags()
            self.prepare_and_send_reports()
            application_support.clear_application_tags()
            return response

        return wrapper

    call = __call__

    def execute_hook(self, name, data):
        if name == 'after:invocation':
            [plugin.hooks[name](data) for plugin in reversed(self.plugins) if hasattr(plugin, 'hooks') \
                                                                                and name in plugin.hooks]
        else:
            [plugin.hooks[name](data) for plugin in self.plugins if hasattr(plugin, 'hooks') and name in plugin.hooks]

    def check_and_handle_warmup_request(self, event):

        # Check whether it is empty request which is used as default warmup request
        if not event:
            print("Received warmup request as empty message. " +
                  "Handling with 90 milliseconds delay ...")
            time.sleep(0.1)
            return True
        else:
            if isinstance(event, str):
                # Check whether it is warmup request
                if event.startswith('#warmup'):
                    delayTime = 90
                    args = event[len('#warmup'):].strip().split()
                    # Warmup messages are in '#warmup wait=<waitTime>' format
                    # Iterate over all warmup arguments
                    for arg in args:
                        argParts = arg.split('=')
                        # Check whether argument is in key=value format
                        if len(argParts) == 2:
                            argName = argParts[0]
                            argValue = argParts[1]
                            # Check whether argument is "wait" argument
                            # which specifies extra wait time before returning from request
                            if argName == 'wait':
                                waitTime = int(argValue)
                                delayTime += waitTime
                    print("Received warmup request as warmup message. " +
                          "Handling with " + str(delayTime) + " milliseconds delay ...")
                    time.sleep(delayTime / 1000)
                    return True
            return False

    def timeout_handler(self, signum, frame):
        current_thread = threading.current_thread().__class__.__name__
        if current_thread == '_MainThread' and signum == signal.SIGALRM:
            self.plugin_context['timeout'] = True
            self.plugin_context['error'] = TimeoutError('Task timed out')
            self.prepare_and_send_reports()

    def prepare_and_send_reports(self):
        self.execute_hook('after:invocation', self.plugin_context)
        self.reporter.send_report()
