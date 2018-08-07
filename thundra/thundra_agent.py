import signal
import threading
from functools import wraps
import time
import uuid
import logging

from thundra import constants
from thundra.plugins.invocation.invocation_plugin import InvocationPlugin
from thundra.plugins.log.log_plugin import LogPlugin
from thundra.plugins.metric.metric_plugin import MetricPlugin
from thundra.plugins.trace.trace_plugin import TracePlugin
from thundra.reporter import Reporter

import thundra.utils as utils
from thundra.serializable import Serializable

logger = logging.getLogger(__name__)

class Thundra:
    def __init__(self,
                 api_key=None,
                 disable_trace=False,
                 disable_metric=False,
                 disable_log=False,
                 request_skip=False,
                 response_skip=False):

        constants.REQUEST_COUNT = 0

        self.plugins = []
        api_key_from_environment_variable = utils.get_environment_variable(constants.THUNDRA_APIKEY)
        self.api_key = api_key_from_environment_variable if api_key_from_environment_variable is not None else api_key
        if self.api_key is None:
            logger.error('Please set thundra_apiKey from environment variables in order to use Thundra')
        self.plugins.append(InvocationPlugin())
        self.data = {}

        disable_trace_by_env = utils.get_environment_variable(constants.THUNDRA_DISABLE_TRACE)
        if not utils.should_disable(disable_trace_by_env, disable_trace):
            self.plugins.append(TracePlugin())

        disable_metric_by_env = utils.get_environment_variable(constants.THUNDRA_DISABLE_METRIC)
        if not utils.should_disable(disable_metric_by_env, disable_metric):
            self.plugins.append(MetricPlugin())

        disable_log_by_env = utils.get_environment_variable(constants.THUNDRA_DISABLE_LOG)
        if not utils.should_disable(disable_log_by_env, disable_log):
            self.plugins.append(LogPlugin())

        audit_request_skip_by_env = utils.get_environment_variable(constants.THUNDRA_LAMBDA_TRACE_REQUEST_SKIP)
        self.data['request_skipped'] = utils.should_disable(audit_request_skip_by_env, request_skip)

        audit_response_skip_by_env = utils.get_environment_variable(constants.THUNDRA_LAMBDA_TRACE_RESPONSE_SKIP)
        self.response_skipped = utils.should_disable(audit_response_skip_by_env, response_skip)

        is_warmup_aware_by_env = utils.get_environment_variable(constants.THUNDRA_LAMBDA_WARMUP_WARMUPAWARE)
        self.warmup_aware = utils.should_disable(is_warmup_aware_by_env)

        timeout_margin = utils.get_environment_variable(constants.THUNDRA_LAMBDA_TIMEOUT_MARGIN)
        self.timeout_margin = int(timeout_margin) if timeout_margin is not None else 0
        if self.timeout_margin <= 0:
            self.timeout_margin = constants.DEFAULT_LAMBDA_TIMEOUT_MARGIN
            logger.warning('Timeout margin is set to default value (' + str(constants.DEFAULT_LAMBDA_TIMEOUT_MARGIN) +
                           ') since nonpositive value cannot be given')

        self.reporter = Reporter(self.api_key)

    def __call__(self, original_func):

        is_thundra_disabled_by_env = utils.get_environment_variable(constants.THUNDRA_DISABLE)
        should_disable_thundra = utils.should_disable(is_thundra_disabled_by_env)
        if should_disable_thundra:
            return original_func

        self.data['reporter'] = self.reporter

        @wraps(original_func)
        def wrapper(event, context):
            if self.warmup_aware and self.check_and_handle_warmup_request(event):
                constants.REQUEST_COUNT += 1
                return None

            self.data['event'] = event
            self.data['context'] = context

            self.data['transactionId'] = str(uuid.uuid4())

            self.execute_hook('before:invocation', self.data)
            if threading.current_thread().__class__.__name__ == '_MainThread':
                signal.signal(signal.SIGALRM, self.timeout_handler)

                if hasattr(context, 'get_remaining_time_in_millis'):
                    timeout_duration = context.get_remaining_time_in_millis() - self.timeout_margin
                    if timeout_duration <= 0:
                        timeout_duration = constants.DEFAULT_LAMBDA_TIMEOUT_MARGIN
                        logger.warning('Given timeout margin is bigger than lambda timeout duration and '
                                       'since the difference is negative, it is set to default value (' +
                                       str(constants.DEFAULT_LAMBDA_TIMEOUT_MARGIN) + ')')
                    signal.setitimer(signal.ITIMER_REAL, timeout_duration/1000.0)
            try:
                response = original_func(event, context)
                if self.response_skipped is False:
                    resp = response
                    if hasattr(response, '__dict__'):
                        if isinstance(response, Serializable):
                            resp = response.serialize()
                        else:
                            resp = 'Not json serializable object'
                    self.data['response'] = resp
            except Exception as e:
                self.data['error'] = e
                self.prepare_and_send_reports()
                raise e
            finally:
                if threading.current_thread().__class__.__name__ == '_MainThread':
                    signal.setitimer(signal.ITIMER_REAL, 0)
            self.prepare_and_send_reports()
            return response

        return wrapper

    call = __call__

    def execute_hook(self, name, data):
        [plugin.hooks[name](data) for plugin in self.plugins if hasattr(plugin, 'hooks') and name in plugin.hooks]

    def check_and_handle_warmup_request(self, event):

        # Check whether it is empty request which is used as default warmup request
        if not event:
            print("Received warmup request as empty message. " +
                  "Handling with 100 milliseconds delay ...")
            time.sleep(0.1)
            return True
        else:
            if isinstance(event, str):
                # Check whether it is warmup request
                if event.startswith('#warmup'):
                    delayTime = 100
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
            self.data['timeout'] = True
            # Pass it to trace plugin, ES currently doesn't allow boolean so pass it as a string.
            self.data['timeoutString'] = 'true'
            self.data['error'] = TimeoutError('Task timed out')
            self.prepare_and_send_reports()

    def prepare_and_send_reports(self):
        self.execute_hook('after:invocation', self.data)
        self.reporter.send_report()

