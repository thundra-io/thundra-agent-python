import signal
import threading
import time
import logging
from functools import wraps

from thundra.reporter import Reporter
from thundra.plugins.log.log_plugin import LogPlugin
from thundra.plugins.trace.patcher import ImportPatcher
from thundra.plugins.invocation import invocation_support
from thundra.plugins.trace.trace_plugin import TracePlugin
from thundra.plugins.metric.metric_plugin import MetricPlugin
from thundra import constants, application_support, config
from thundra.plugins.invocation.invocation_plugin import InvocationPlugin

logger = logging.getLogger(__name__)

class Thundra:

    def __init__(self,
                 api_key=None,
                 disable_trace=False,
                 disable_metric=False,
                 disable_log=False):

        constants.REQUEST_COUNT = 0
        self.plugins = []
        
        self.api_key = config.api_key(api_key)
        if self.api_key is None:
            logger.error('Please set "thundra_apiKey" from environment variables in order to use Thundra')

        if not config.trace_disabled(disable_trace):
            self.plugins.append(TracePlugin())

        self.plugins.append(InvocationPlugin())
        self.plugin_context = {}

        if not config.metric_disabled(disable_metric):
            self.plugins.append(MetricPlugin())

        if not config.log_disabled(disable_log):
            self.plugins.append(LogPlugin())

        self.timeout_margin = config.timeout_margin()
        self.reporter = Reporter(self.api_key)

        if not config.trace_instrument_disabled():
            self.import_patcher = ImportPatcher()

    def __call__(self, original_func):
        if config.thundra_disabled():
            return original_func

        @wraps(original_func)
        def wrapper(event, context):
            before_done = False
            after_done = False

            # Clear plugin context for each invocation
            self.plugin_context = {}
            self.plugin_context['reporter'] = self.reporter
            application_support.parse_application_info(context)
            invocation_support.parse_invocation_info(context)
            
            # Before running user's handler
            try:
                if self.check_and_handle_warmup_request(event):
                    return None

                constants.REQUEST_COUNT += 1

                self.plugin_context['request'] = event
                self.plugin_context['context'] = context
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
                before_done = True
            except Exception as e:
                logger.error("Error during the before part of Thundra: {}".format(e))
                before_done = False
            
            # Invoke user handler
            if before_done:
                try:
                    response = original_func(event, context)
                    self.plugin_context['response'] = response
                except Exception as e:
                    try:
                        self.plugin_context['error'] = e
                        self.prepare_and_send_reports()
                        after_done = True
                    except Exception as e_in:
                        logger.error("Error during the after part of Thundra: {}".format(e_in))
                        self.reporter.reports.clear()
                        after_done = False
                        pass
                    raise e
                finally:
                    self.stop_timer()
            else:
                self.stop_timer()
                self.reporter.reports.clear()
                return original_func(event, context)
            
            # After having run the user's handler
            if before_done and not after_done:
                try:
                    self.prepare_and_send_reports()
                except Exception as e:
                    logger.error("Error during the after part of Thundra: {}".format(e))
                    self.reporter.reports.clear()
                
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

    def stop_timer(self):
        if threading.current_thread().__class__.__name__ == '_MainThread':
            signal.setitimer(signal.ITIMER_REAL, 0)

    def prepare_and_send_reports(self):
        self.execute_hook('after:invocation', self.plugin_context)
        self.reporter.send_report()
