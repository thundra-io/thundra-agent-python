from functools import wraps
import time

from thundra import constants
from thundra.plugins.trace.trace_plugin import TracePlugin
from thundra.reporter import Reporter

import thundra.utils as utils


class Thundra:
    def __init__(self, api_key=None, disable_trace=False, request_skip=False, response_skip=False):

        constants.REQUEST_COUNT = 0

        self.plugins = []
        api_key_from_environment_variable = utils.get_thundra_apikey()
        self.api_key = api_key_from_environment_variable if api_key_from_environment_variable is not None else api_key
        if self.api_key is None:
            raise Exception('Please set thundra_apiKey from environment variables in order to use Thundra')
        self.data = {}

        disable_trace_by_env = utils.is_thundra_trace_disabled()
        if not utils.should_disable(disable_trace_by_env, disable_trace):
            self.plugins.append(TracePlugin())

        audit_request_skip_by_env = utils.is_thundra_lambda_audit_request_skipped()
        self.data['request_skipped'] = utils.should_disable(audit_request_skip_by_env, request_skip)

        audit_response_skip_by_env = utils.is_thundra_lambda_audit_response_skipped()
        self.response_skipped = utils.should_disable(audit_response_skip_by_env, response_skip)

        self.reporter = Reporter(self.api_key)

    def __call__(self, original_func):

        should_disable_thundra = utils.is_thundra_disabled()
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
                if self.response_skipped is not True:
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


