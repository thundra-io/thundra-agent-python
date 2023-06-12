from functools import wraps
import logging
from catchpoint import constants

from catchpoint.opentracing.tracer import CatchpointTracer
from catchpoint.wrappers.base_wrapper import BaseWrapper

from catchpoint.config.config_provider import ConfigProvider
from catchpoint.context.execution_context_manager import ExecutionContextManager
from catchpoint.context.plugin_context import PluginContext
from catchpoint.application.global_application_info_provider import GlobalApplicationInfoProvider
from catchpoint.context.tracing_execution_context_provider import TracingExecutionContextProvider
from catchpoint.wrappers.fastapi import fastapi_executor
from catchpoint.config import config_names
from catchpoint.wrappers import wrapper_utils, web_wrapper_utils

import traceback


logger = logging.getLogger(__name__)


class FastapiWrapper(BaseWrapper):    
    __instance = None
    
    @staticmethod
    def get_instance():
        return FastapiWrapper() if FastapiWrapper.__instance is None else FastapiWrapper.__instance

    def __init__(self, api_key=None, disable_trace=False, disable_metric=True, disable_log=True, opts=None):
        super(FastapiWrapper, self).__init__(api_key, disable_trace, disable_metric, disable_log, opts)
        self.application_info_provider = GlobalApplicationInfoProvider()
        ExecutionContextManager.set_provider(TracingExecutionContextProvider())
        self.plugin_context = PluginContext(application_info=self.application_info_provider.get_application_info(),
                                            request_count=0,
                                            executor=fastapi_executor,
                                            api_key=self.api_key)

        self.plugins = wrapper_utils.initialize_plugins(self.plugin_context, disable_trace, disable_metric, disable_log,
                                                        config=self.config)

        web_wrapper_utils.update_application_info(self.application_info_provider, self.plugin_context.application_info,
                                                  constants.ClassNames['FASTAPI'])

        FastapiWrapper.__instance = self

    def before_request(self, request, req_body):
        execution_context = wrapper_utils.create_execution_context()
        execution_context.platform_data["request"] = request
        execution_context.platform_data["request"]["body"] = req_body

        self.plugin_context.request_count += 1
        self.execute_hook("before:invocation", execution_context)

        return execution_context


    def after_request(self, execution_context):
        self.prepare_and_send_reports_async(execution_context)

    def error_handler(self, error, execution_context):
        if error:
            execution_context.error = error

        self.prepare_and_send_reports_async(execution_context)
        
        

    def __call__(self, original_func):

        import inspect
        if hasattr(original_func, "_catchpoint_wrapped") or ConfigProvider.get(config_names.CATCHPOINT_DISABLE, False):
            return original_func

        @wraps(original_func)
        async def wrapper(*args, **kwargs):
            request = kwargs.get("request")
            if request is None or request.scope.get('_catchpoint_wrapped', False):
                if inspect.iscoroutinefunction(original_func):
                    return await original_func(*args, **kwargs)
                else:
                    return original_func(*args, **kwargs)

            request.scope['_catchpoint_wrapped'] = True
            try:
                req_body = request._body if hasattr(request, "_body") else None
                request.scope["catchpoint_execution_context"] = self.before_request(request.scope, req_body)
                execution_context = request.scope["catchpoint_execution_context"]
            except Exception as e:
                logger.error('Error during the before part of Catchpoint: {}'.format(e))
                if inspect.iscoroutinefunction(original_func):
                    return await original_func(*args, **kwargs)
                else:
                    return original_func(*args, **kwargs)

            response = None
            try:
                if inspect.iscoroutinefunction(original_func):
                    response = await original_func(*args, **kwargs)
                else:
                    response = original_func(*args, **kwargs)
            except Exception as e:
                try:
                    error = {
                        'type': type(e).__name__,
                        'message': str(e),
                        'traceback': traceback.format_exc()
                    }
                    self.error_handler(error, execution_context)
                except Exception as e_in:
                    logger.error("Error during the after part of Catchpoint: {}".format(e_in))
                raise e

            try:
                execution_context.response = response
                self.after_request(execution_context)
            except Exception as e:
                logger.error("Error during the after part of Catchpoint: {}".format(e))
            return response

        setattr(wrapper, '_catchpoint_wrapped', True)
        return wrapper