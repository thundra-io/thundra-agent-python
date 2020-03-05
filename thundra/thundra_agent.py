import subprocess
import time
import logging
import os
from functools import wraps

from thundra.reporter import Reporter
from thundra.plugins.log.log_plugin import LogPlugin
from thundra.plugins.invocation import invocation_support
from thundra.plugins.trace.trace_plugin import TracePlugin
from thundra.plugins.metric.metric_plugin import MetricPlugin
from thundra import constants, application_support, config
from thundra.plugins.invocation.invocation_plugin import InvocationPlugin
from thundra.integrations import handler_wrappers
from thundra.plugins.log.thundra_logger import debug_logger
from thundra.compat import PY2, TimeoutError
from thundra.timeout import Timeout


logger = logging.getLogger(__name__)

if not PY2:
    from thundra.plugins.trace.patcher import ImportPatcher


class Thundra:

    def __init__(self,
                 api_key=None,
                 disable_trace=False,
                 disable_metric=True,
                 disable_log=True):

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
        self.debugger_process = None

        if not config.trace_instrument_disabled():
            if not PY2:
                self.import_patcher = ImportPatcher()

            # Pass thundra instance to integration for wrapping handler wrappers
            handler_wrappers.patch_modules(self)
        self.ptvsd_imported = False
        if config.debugger_enabled():
            self.initialize_debugger()

    def __call__(self, original_func):
        if hasattr(original_func, "thundra_wrapper") or config.thundra_disabled():
            return original_func

        @wraps(original_func)
        def wrapper(event, context):
            before_done = False
            after_done = False

            # Clear plugin context for each invocation
            self.plugin_context = {'reporter': self.reporter}
            application_support.parse_application_info(context)
            invocation_support.parse_invocation_info(context)

            # Before running user's handler
            try:
                if config.warmup_aware() and self.check_and_handle_warmup_request(event):
                    return None

                constants.REQUEST_COUNT += 1

                self.plugin_context['request'] = event
                self.plugin_context['context'] = context
                self.execute_hook('before:invocation', self.plugin_context)

                timeout_duration = self.get_timeout_duration(context)
                before_done = True
            except Exception as e:
                logger.error("Error during the before part of Thundra: {}".format(e))
                before_done = False

            # Invoke user handler
            if before_done:
                try:
                    response = None
                    with Timeout(timeout_duration, self.timeout_handler):
                        if config.debugger_enabled() and self.ptvsd_imported:
                            self.start_debugger_tracing()

                        response = original_func(event, context)
                        self.plugin_context['response'] = response
                except Exception as e:
                    try:
                        self.plugin_context['error'] = e
                        self.prepare_and_send_reports()
                        after_done = True
                    except Exception as e_in:
                        logger.error("Error during the after part of Thundra: {}".format(e_in))
                        self.reporter.reports = []
                        after_done = False
                        pass
                    raise e
                finally:
                    if config.debugger_enabled() and self.ptvsd_imported:
                        self.stop_debugger_tracing()
            else:
                self.reporter.reports = []
                return original_func(event, context)

            # After having run the user's handler
            if before_done and not after_done:
                try:
                    self.prepare_and_send_reports()
                except Exception as e:
                    logger.error("Error during the after part of Thundra: {}".format(e))
                    self.reporter.reports = []

            return response

        setattr(wrapper, 'thundra_wrapper', True)
        return wrapper

    call = __call__

    def initialize_debugger(self):
        if PY2:
            logger.error("Online debugging not supported in python2.7. Supported versions: 3.6, 3.7, 3.8")
            return
        try:
            import ptvsd
            self.ptvsd_imported = True
        except Exception as e:
            logger.error("Could not import ptvsd. Thundra ptvsd layer must be added")


    def start_debugger_tracing(self):
        try:
            import ptvsd
            ptvsd.tracing(True)

            ptvsd.enable_attach(address=("localhost", config.debugger_port()))
            if not self.debugger_process:
                env = os.environ.copy()
                env['BROKER_HOST'] = str(config.debugger_broker_host())
                env['BROKER_PORT'] = str(config.debugger_broker_port())
                env['DEBUGGER_PORT'] = str(config.debugger_port())
                env['AUTH_TOKEN'] = str(config.debugger_auth_token())
                env['SESSION_NAME'] = str(config.debugger_session_name())
                context = self.plugin_context["context"]
                if hasattr(context, 'get_remaining_time_in_millis'):
                    env['SESSION_TIMEOUT'] = str(context.get_remaining_time_in_millis() + int(time.time()*1000.0))
                self.debugger_process = subprocess.Popen(["python", "thundra/debug/bridge.py"], stdout=subprocess.PIPE, stdin=subprocess.PIPE, env=env)

            start_time = time.time()
            debug_process_running = True
            while time.time() < (start_time + config.debugger_max_wait_time()/1000) and not ptvsd.is_attached():
                if self.debugger_process.poll() is None:
                    ptvsd.wait_for_attach(0.01)
                else:
                    debug_process_running = False
                    break

            if not ptvsd.is_attached():
                if debug_process_running:
                    logger.error('Couldn\'t complete debugger handshake in {} milliseconds.'.format(config.debugger_max_wait_time()))
                ptvsd.tracing(False)
            else:
                ptvsd.tracing(True)

        except Exception as e:
            logger.error("error while setting tracing true to debugger using ptvsd: {}".format(e))

    def stop_debugger_tracing(self):
        try:
            import ptvsd
            ptvsd.tracing(False)
            from ptvsd.attach_server import debugger_attached
            debugger_attached.clear()
        except Exception as e:
            logger.error("error while setting tracing false to debugger using ptvsd: {}".format(e))

        try:
            if self.debugger_process:
                o, e = self.debugger_process.communicate(b"fin\n")
                debug_logger("Thundra debugger process output: {}".format(o.decode("utf-8")))
                self.debugger_process = None
        except Exception as e:
            self.debugger_process = None
            logger.error("error while killing proxy process for debug: {}".format(e))

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

    def get_timeout_duration(self, context):
        timeout_duration = 0
        if hasattr(context, 'get_remaining_time_in_millis'):
            timeout_duration = context.get_remaining_time_in_millis() - self.timeout_margin
            if timeout_duration <= 0:
                timeout_duration = context.get_remaining_time_in_millis() - \
                                    constants.DEFAULT_LAMBDA_TIMEOUT_MARGIN
                logger.warning('Given timeout margin is bigger than lambda timeout duration and '
                                'since the difference is negative, it is set to default value (' +
                                str(constants.DEFAULT_LAMBDA_TIMEOUT_MARGIN) + ')')

        return timeout_duration/1000.0

    def timeout_handler(self):
            self.plugin_context['timeout'] = True
            self.plugin_context['error'] = TimeoutError('Task timed out')
            self.prepare_and_send_reports()

    def prepare_and_send_reports(self):
        self.execute_hook('after:invocation', self.plugin_context)
        self.reporter.send_report()
