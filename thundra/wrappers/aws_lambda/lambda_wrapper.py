import logging
import os
import subprocess
import time
import traceback
import uuid
from functools import wraps

from thundra import constants
from thundra.application.global_application_info_provider import GlobalApplicationInfoProvider
from thundra.compat import PY2, TimeoutError
from thundra.config import config_names
from thundra.config.config_provider import ConfigProvider
from thundra.context.execution_context import ExecutionContext
from thundra.context.execution_context_manager import ExecutionContextManager
from thundra.context.global_execution_context_provider import GlobalExecutionContextProvider
from thundra.context.plugin_context import PluginContext
from thundra.integrations import handler_wrappers
from thundra.plugins.config.thundra_config import ThundraConfig
from thundra.plugins.log.thundra_logger import debug_logger
from thundra.reporter import Reporter
from thundra.timeout import Timeout
from thundra.wrappers import wrapper_utils
from thundra.wrappers.aws_lambda import LambdaApplicationInfoProvider
from thundra.wrappers.aws_lambda import lambda_executor

logger = logging.getLogger(__name__)

if not PY2:
    from thundra.plugins.trace.patcher import ImportPatcher


class LambdaWrapper:

    def __init__(self,
                 api_key=None,
                 disable_trace=False,
                 disable_metric=True,
                 disable_log=True,
                 opts=None):
        config = ThundraConfig()
        if opts is not None:
            config = ThundraConfig(opts)

        self.api_key = ConfigProvider.get(config_names.THUNDRA_APIKEY, api_key)
        if not self.api_key:
            self.api_key = config.api_key
        if self.api_key is None:
            logger.error('Please set "thundra_apiKey" from environment variables in order to use Thundra')

        self.application_info_provider = GlobalApplicationInfoProvider(LambdaApplicationInfoProvider())
        self.plugin_context = PluginContext(application_info=self.application_info_provider.get_application_info(),
                                            request_count=0,
                                            executor=lambda_executor,
                                            api_key=self.api_key)

        ExecutionContextManager.set_provider(GlobalExecutionContextProvider())
        self.plugins = wrapper_utils.initialize_plugins(self.plugin_context, disable_trace, disable_metric, disable_log,
                                                        config)

        self.timeout_margin = ConfigProvider.get(config_names.THUNDRA_LAMBDA_TIMEOUT_MARGIN,
                                                 constants.DEFAULT_LAMBDA_TIMEOUT_MARGIN)
        self.reporter = Reporter(self.api_key)
        self.debugger_process = None

        if not ConfigProvider.get(config_names.THUNDRA_TRACE_INSTRUMENT_DISABLE):
            if not PY2:
                self.import_patcher = ImportPatcher()
            # Pass thundra instance to integration for wrapping handler wrappers
            handler_wrappers.patch_modules(self)

        self.ptvsd_imported = False
        if ConfigProvider.get(config_names.THUNDRA_LAMBDA_DEBUGGER_ENABLE):
            self.initialize_debugger()

    def __call__(self, original_func):
        if hasattr(original_func, "thundra_wrapper") or ConfigProvider.get(config_names.THUNDRA_DISABLE, False):
            return original_func

        @wraps(original_func)
        def wrapper(event, context):
            application_name = self.plugin_context.application_info.get('applicationName')
            self.application_info_provider.update({
                'applicationId': LambdaApplicationInfoProvider.get_application_id(context,
                                                                                  application_name=application_name)
            })

            # Execution context initialization
            trace_id = str(uuid.uuid4())
            transaction_id = str(uuid.uuid4())
            execution_context = ExecutionContext(trace_id=trace_id, transaction_id=transaction_id)
            execution_context.start_timestamp = int(time.time() * 1000)
            execution_context.platform_data['originalEvent'] = event
            execution_context.platform_data['originalContext'] = context
            ExecutionContextManager.set(execution_context)

            # Before running user's handler
            try:
                if ConfigProvider.get(config_names.THUNDRA_LAMBDA_WARMUP_WARMUPAWARE,
                                      False) and self.check_and_handle_warmup_request(event):
                    return None

                self.plugin_context.request_count += 1
                self.execute_hook('before:invocation', execution_context)

                timeout_duration = self.get_timeout_duration(context)
            except Exception as e:
                logger.error("Error during the before part of Thundra: {}".format(e))
                return original_func(event, context)

            # Invoke user handler
            try:
                response = None
                with Timeout(timeout_duration, self.timeout_handler, execution_context):
                    if ConfigProvider.get(config_names.THUNDRA_LAMBDA_DEBUGGER_ENABLE) and self.ptvsd_imported:
                        self.start_debugger_tracing()

                    response = original_func(event, context)
                    execution_context.response = response
            except Exception as e:
                try:
                    execution_context.error = {
                        'type': type(e).__name__,
                        'message': str(e),
                        'traceback': traceback.format_exc()
                    }
                    self.prepare_and_send_reports(execution_context)
                except Exception as e_in:
                    logger.error("Error during the after part of Thundra: {}".format(e_in))
                    pass
                raise e
            finally:
                if ConfigProvider.get(config_names.THUNDRA_LAMBDA_DEBUGGER_ENABLE) and self.ptvsd_imported:
                    self.stop_debugger_tracing()

            # After having run the user's handler
            try:
                self.prepare_and_send_reports(execution_context)
            except Exception as e:
                logger.error("Error during the after part of Thundra: {}".format(e))

            ExecutionContextManager.clear()
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

            ptvsd.enable_attach(address=("localhost", ConfigProvider.get(config_names.THUNDRA_LAMBDA_DEBUGGER_PORT)))
            if not self.debugger_process:
                env = os.environ.copy()
                env['BROKER_HOST'] = str(ConfigProvider.get(config_names.THUNDRA_LAMBDA_DEBUGGER_BROKER_HOST))
                env['BROKER_PORT'] = str(ConfigProvider.get(config_names.THUNDRA_LAMBDA_DEBUGGER_BROKER_PORT))
                env['DEBUGGER_PORT'] = str(ConfigProvider.get(config_names.THUNDRA_LAMBDA_DEBUGGER_PORT))
                env['AUTH_TOKEN'] = str(ConfigProvider.get(config_names.THUNDRA_LAMBDA_DEBUGGER_AUTH_TOKEN))
                env['SESSION_NAME'] = str(ConfigProvider.get(config_names.THUNDRA_LAMBDA_DEBUGGER_SESSION_NAME))
                context = self.plugin_context["context"]
                if hasattr(context, 'get_remaining_time_in_millis'):
                    env['SESSION_TIMEOUT'] = str(context.get_remaining_time_in_millis() + int(time.time() * 1000.0))

                debug_bridge_file_path = os.path.join(os.path.dirname(__file__), 'debug/bridge.py')
                self.debugger_process = subprocess.Popen(["python", debug_bridge_file_path], stdout=subprocess.PIPE,
                                                         stdin=subprocess.PIPE, env=env)

            start_time = time.time()
            debug_process_running = True
            while time.time() < (start_time + ConfigProvider.get(config_names.THUNDRA_LAMBDA_DEBUGGER_WAIT_MAX) / 1000) \
                    and not ptvsd.is_attached():
                if self.debugger_process.poll() is None:
                    ptvsd.wait_for_attach(0.01)
                else:
                    debug_process_running = False
                    break

            if not ptvsd.is_attached():
                if debug_process_running:
                    logger.error('Couldn\'t complete debugger handshake in {} milliseconds.' \
                                 .format(ConfigProvider.get(config_names.THUNDRA_LAMBDA_DEBUGGER_WAIT_MAX)))
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

        return timeout_duration / 1000.0

    def timeout_handler(self, execution_context):
        execution_context.timeout = True
        execution_context.error = TimeoutError('Task timed out')
        self.prepare_and_send_reports(execution_context)

    def prepare_and_send_reports(self, execution_context):
        self.execute_hook('after:invocation', execution_context)
        self.reporter.send_report(execution_context.reports)
