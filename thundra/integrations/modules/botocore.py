import wrapt

from thundra.config import config_names
from thundra.config.config_provider import ConfigProvider
from thundra.integrations.base_integration import BaseIntegration
from thundra.integrations.modules.requests import _wrapper as request_wrapper

import thundra.integrations.botocore

INTEGRATIONS = {
    class_obj.CLASS_TYPE: class_obj()
    for class_obj in BaseIntegration.__subclasses__()
}


def _wrapper(wrapped, instance, args, kwargs):
    integration_name = instance.__class__.__name__.lower()

    if integration_name in INTEGRATIONS:
        return INTEGRATIONS[integration_name].run_and_trace(
            wrapped,
            instance,
            args,
            kwargs
        )

    return INTEGRATIONS['default'].run_and_trace(
        wrapped,
        instance,
        args,
        kwargs
    )


def patch():
    if not ConfigProvider.get(config_names.THUNDRA_TRACE_INTEGRATIONS_AWS_DISABLE):
        wrapt.wrap_function_wrapper(
            'botocore.client',
            'BaseClient._make_api_call',
            _wrapper
        )
    if not ConfigProvider.get(config_names.THUNDRA_TRACE_INTEGRATIONS_HTTP_DISABLE):
        try:
            wrapt.wrap_function_wrapper(
                'botocore.vendored.requests',
                'Session.send',
                request_wrapper
            )
        except Exception:
            # Vendored version of requests is removed from botocore
            pass
