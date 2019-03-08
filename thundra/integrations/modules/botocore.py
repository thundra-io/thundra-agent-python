import wrapt
import thundra.integrations.botocore
from thundra import config
from thundra.integrations.base_integration import BaseIntegration
from thundra.integrations.modules.requests import _wrapper as request_wrapper

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

    return wrapped(*args, **kwargs)

def patch():
    if not config.aws_integration_disabled():
        wrapt.wrap_function_wrapper(
            'botocore.client',
            'BaseClient._make_api_call',
            _wrapper
        )
    if not config.http_integration_disabled():
        wrapt.wrap_function_wrapper(
            'botocore.vendored.requests',
            'Session.send',
            request_wrapper
        )
