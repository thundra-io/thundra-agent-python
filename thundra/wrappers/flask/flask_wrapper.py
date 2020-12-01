import logging
import traceback
from functools import wraps

from thundra import constants
from thundra.application.global_application_info_provider import GlobalApplicationInfoProvider
from thundra.config import config_names
from thundra.config.config_provider import ConfigProvider
from thundra.context.execution_context_manager import ExecutionContextManager
from thundra.context.plugin_context import PluginContext
from thundra.context.tracing_execution_context_provider import TracingExecutionContextProvider
from thundra.wrappers import wrapper_utils, web_wrapper_utils
from thundra.wrappers.base_wrapper import BaseWrapper
from thundra.wrappers.flask import flask_executor

try:
    from flask import request, g
except ImportError:
    request = None
    g = None

logger = logging.getLogger(__name__)


class FlaskWrapper(BaseWrapper):

    def __init__(self, api_key=None, disable_trace=False, disable_metric=True, disable_log=True, opts=None):
        super(FlaskWrapper, self).__init__(api_key, disable_trace, disable_metric, disable_log, opts)
        self.application_info_provider = GlobalApplicationInfoProvider()
        ExecutionContextManager.set_provider(TracingExecutionContextProvider())
        self.plugin_context = PluginContext(application_info=self.application_info_provider.get_application_info(),
                                            request_count=0,
                                            executor=flask_executor,
                                            api_key=self.api_key)

        self.plugins = wrapper_utils.initialize_plugins(self.plugin_context, disable_trace, disable_metric, disable_log,
                                                        config=self.config)

        web_wrapper_utils.update_application_info(self.application_info_provider, self.plugin_context.application_info,
                                                  constants.ClassNames['FLASK'])

    def before_request(self, _request):
        # Execution context initialization
        execution_context = wrapper_utils.create_execution_context()
        execution_context.platform_data['request'] = _request

        # Execute plugin hooks before running user's handler
        self.plugin_context.request_count += 1
        self.execute_hook('before:invocation', execution_context)

        if g is not None:
            g.thundra_execution_context = execution_context

        return execution_context

    def after_request(self, response):
        try:
            if g is not None and hasattr(g, 'thundra_execution_context'):
                execution_context = g.thundra_execution_context
                if response:
                    execution_context.response = response
        except Exception as e:
            logger.error('Error setting response to context for Thundra: {}'.format(e))
        return response

    def teardown_request(self, exception=None):
        try:
            if g is not None and hasattr(g, 'thundra_execution_context'):
                execution_context = g.thundra_execution_context
                if exception:
                    execution_context.error = exception
                self.prepare_and_send_reports_async(execution_context)
        except Exception as e:
            logger.error('Error during the request teardown of Thundra: {}'.format(e))

    def __call__(self, original_func):
        if hasattr(original_func, "_thundra_wrapped") or ConfigProvider.get(config_names.THUNDRA_DISABLE, False):
            return original_func

        @wraps(original_func)
        def wrapper(*args, **kwargs):
            if request is None or getattr(request, '_thundra_wrapped', False):
                return original_func(*args, **kwargs)
            setattr(request, '_thundra_wrapped', True)
            try:
                execution_context = self.before_request(request)
            except Exception as e:
                logger.error('Error during the before part of Thundra: {}'.format(e))
                return original_func(*args, **kwargs)

            response = None
            # Invoke user handler
            try:
                response = original_func(*args, **kwargs)
                execution_context.response = response
            except Exception as e:
                try:
                    error = {
                        'type': type(e).__name__,
                        'message': str(e),
                        'traceback': traceback.format_exc()
                    }
                    self.teardown_request(error)
                except Exception as e_in:
                    logger.error("Error during the after part of Thundra: {}".format(e_in))
                raise e

            try:
                self.teardown_request()
            except Exception as e:
                logger.error("Error during the after part of Thundra: {}".format(e))
            return response

        setattr(wrapper, '_thundra_wrapped', True)
        return wrapper

    call = __call__
