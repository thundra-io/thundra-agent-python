from functools import wraps
import time
import uuid

from thundra import constants
from thundra.plugins.invocation.invocation_plugin import InvocationPlugin
from thundra.plugins.metric.metric_plugin import MetricPlugin
from thundra.plugins.trace.trace_plugin import TracePlugin
from thundra.reporter import Reporter

import thundra.utils as utils


class Thundra:
    def __init__(self, api_key=None, disable_trace=False, disable_metric=False, request_skip=False, response_skip=False):

        constants.REQUEST_COUNT = 0

        self.plugins = []
        api_key_from_environment_variable = utils.get_environment_variable(constants.THUNDRA_APIKEY)
        self.api_key = api_key_from_environment_variable if api_key_from_environment_variable is not None else api_key
        if self.api_key is None:
            raise Exception('Please set thundra_apiKey from environment variables in order to use Thundra')
        self.plugins.append(InvocationPlugin())
        self.data = {}

        transaction_id = str(uuid.uuid4())
        self.data['transactionId'] = transaction_id

        disable_trace_by_env = utils.get_environment_variable(constants.THUNDRA_DISABLE_TRACE)
        if not utils.should_disable(disable_trace_by_env, disable_trace):
            self.plugins.append(TracePlugin())

        disable_metric_by_env = utils.get_environment_variable(constants.THUNDRA_DISABLE_METRIC)
        if not utils.should_disable(disable_metric_by_env, disable_metric):
            self.plugins.append(MetricPlugin())

        audit_request_skip_by_env = utils.get_environment_variable(constants.THUNDRA_LAMBDA_TRACE_REQUEST_SKIP)
        self.data['request_skipped'] = utils.should_disable(audit_request_skip_by_env, request_skip)

        audit_response_skip_by_env = utils.get_environment_variable(constants.THUNDRA_LAMBDA_TRACE_RESPONSE_SKIP)
        self.response_skipped = utils.should_disable(audit_response_skip_by_env, response_skip)

        self.reporter = Reporter(self.api_key)

    def __call__(self, original_func):

        is_thundra_disabled_by_env = utils.get_environment_variable(constants.THUNDRA_DISABLE)
        should_disable_thundra = utils.should_disable(is_thundra_disabled_by_env)
        if should_disable_thundra:
            return original_func

        @wraps(original_func)
        def wrapper(event, context):
            if self.checkAndHandleWarmupRequest(event):
                constants.REQUEST_COUNT += 1
                return None
            self.data['reporter'] = self.reporter
            self.data['event'] = event
            self.data['context'] = context
            self.execute_hook('before:invocation', self.data)
            try:
                response = original_func(event, context)
                if self.response_skipped is False:
                    self.data['response'] = response
            except Exception as e:
                self.data['error'] = e
                self.execute_hook('after:invocation', self.data)
                self.reporter.send_report()
                raise e
            self.execute_hook('after:invocation', self.data)
            self.reporter.send_report()
            return response

        return wrapper

    call = __call__

    def execute_hook(self, name, data):
        [plugin.hooks[name](data) for plugin in self.plugins if hasattr(plugin, 'hooks') and name in plugin.hooks]

    def checkAndHandleWarmupRequest(self, event):

        # Check whether it is empty request which is used as default warmup request
        if (not event):
            print("Received warmup request as empty message. " +
                  "Handling with 100 milliseconds delay ...")
            time.sleep(0.1)
            return True
        else:
            if (isinstance(event, str)):
                # Check whether it is warmup request
                if (event.startswith('#warmup')):
                    delayTime = 100
                    args = event[len('#warmup'):].strip().split()
                    # Warmup messages are in '#warmup wait=<waitTime>' format
                    # Iterate over all warmup arguments
                    for arg in args:
                        argParts = arg.split('=')
                        # Check whether argument is in key=value format
                        if (len(argParts) == 2):
                            argName = argParts[0]
                            argValue = argParts[1]
                            # Check whether argument is "wait" argument
                            # which specifies extra wait time before returning from request
                            if (argName == 'wait'):
                                waitTime = int(argValue)
                                delayTime += waitTime
                    print("Received warmup request as warmup message. " +
                          "Handling with " + str(delayTime) + " milliseconds delay ...")
                    time.sleep(delayTime / 1000)
                    return True
            return False


