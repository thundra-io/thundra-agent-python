import logging
import time
import traceback
import uuid
from functools import wraps

from thundra import constants, configure
from thundra.application.global_application_info_provider import GlobalApplicationInfoProvider
from thundra.config import config_names
from thundra.config.config_provider import ConfigProvider
from thundra.context.execution_context import ExecutionContext
from thundra.context.execution_context_manager import ExecutionContextManager
from thundra.context.plugin_context import PluginContext
from thundra.context.tracing_execution_context_provider import TracingExecutionContextProvider
from thundra.plugins.invocation import invocation_support
from thundra.wrappers import wrapper_utils
from thundra.wrappers.base_wrapper import BaseWrapper
from thundra.wrappers.django import django_executor

logger = logging.getLogger(__name__)


class DjangoWrapper(BaseWrapper):

    def __init__(self, api_key=None, disable_trace=False, disable_metric=True, disable_log=True, opts=None):
        try:
            from django.conf import settings
            django_settings = getattr(settings, 'THUNDRA', {})
            configure({'config': django_settings})

            api_key = None
            for var in django_settings:
                if var.lower() == 'thundra.apikey' and not api_key:
                    api_key = django_settings.get(var)
        except:
            pass

        super().__init__(api_key, disable_trace, disable_metric, disable_log, opts)
        self.application_info_provider = GlobalApplicationInfoProvider()
        ExecutionContextManager.set_provider(TracingExecutionContextProvider())
        self.plugin_context = PluginContext(application_info=self.application_info_provider.get_application_info(),
                                            request_count=0,
                                            executor=django_executor,
                                            api_key=self.api_key)

        self.plugins = wrapper_utils.initialize_plugins(self.plugin_context, disable_trace, disable_metric, disable_log,
                                                        config=self.config)

    def before_request(self, request):
        # Set application info
        self.application_info_provider.update({
            'applicationClassName': constants.ClassNames['DJANGO'],
            'applicationDomainName': 'API',
            'applicationInstanceId': self.plugin_context.application_info.get('applicationInstanceId',  str(uuid.uuid4())),
            'applicationId': 'python:{}:{}:{}'.format(constants.ClassNames['DJANGO'],
                                                      self.plugin_context.application_info.get('applicationRegion', ''),
                                                      self.plugin_context.application_info.get('applicationName', ''))
        })

        # Execution context initialization
        transaction_id = str(uuid.uuid4())
        execution_context = ExecutionContext(transaction_id=transaction_id)
        execution_context.start_timestamp = int(time.time() * 1000)
        execution_context.platform_data['request'] = request

        # Execute plugin hooks before running user's handler
        self.plugin_context.request_count += 1
        self.execute_hook('before:invocation', execution_context)

        return execution_context

    def after_request(self, response):
        execution_context = ExecutionContextManager.get()
        if response:
            execution_context.response = response
        self.prepare_and_send_reports(execution_context)

    def process_exception(self, exception):
        execution_context = ExecutionContextManager.get()
        execution_context.error = exception

    def __call__(self, original_func):
        if hasattr(original_func, "thundra_wrapper") or ConfigProvider.get(config_names.THUNDRA_DISABLE, False):
            return original_func

        @wraps(original_func)
        def wrapper(request, *args, **kwargs):
            if getattr(request, '_thundra_wrapped', False):
                return original_func(request, *args, **kwargs)
            setattr(request, '_thundra_wrapped', True)
            try:
                execution_context = self.before_request(request)
                if execution_context.scope:
                    execution_context.scope.span.operation_name = request.resolver_match.route
                    execution_context.trigger_operation_name = request.resolver_match.route
                    invocation_support.set_agent_tag(constants.SpanTags['TRIGGER_OPERATION_NAMES'],
                                                     [request.resolver_match.route])
            except Exception as e:
                logger.error("Error during the before part of Thundra: {}".format(e))
                return original_func(request, *args, **kwargs)

            response = None
            # Invoke user handler
            try:
                response = original_func(request, *args, **kwargs)
            except Exception as e:
                try:
                    execution_context.error = {
                        'type': type(e).__name__,
                        'message': str(e),
                        'traceback': traceback.format_exc()
                    }
                    self.after_request(response)
                except Exception as e_in:
                    logger.error("Error during the after part of Thundra: {}".format(e_in))
                raise e

            try:
                self.after_request(response)
            except Exception as e:
                logger.error("Error during the after part of Thundra: {}".format(e))
            return response

        setattr(wrapper, 'thundra_wrapper', True)
        return wrapper

    call = __call__
