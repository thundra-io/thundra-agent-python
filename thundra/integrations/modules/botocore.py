import wrapt
from thundra.integrations.base_integration import BaseIntegration
from thundra.integrations.modules.requests import _wrapper as request_wrapper
from thundra.integrations import botocore
from thundra import constants
from thundra.config import utils as config_utils


INTEGRATIONS = {
    class_obj.CLASS_TYPE: class_obj()
    for class_obj in BaseIntegration.__subclasses__()
}


def _wrapper(wrapped, instance, args, kwargs):
    integration_name = instance.__class__.__name__.lower()

    print(INTEGRATIONS)
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
    if not config_utils.get_bool_property(constants.THUNDRA_DISABLE_AWS_INTEGRATION):
        wrapt.wrap_function_wrapper(
            'botocore.client',
            'BaseClient._make_api_call',
            _wrapper
        )
    if not config_utils.get_bool_property(constants.THUNDRA_DISABLE_HTTP_INTEGRATION):
        try:
            wrapt.wrap_function_wrapper(
                'botocore.vendored.requests',
                'Session.send',
                request_wrapper
            )
        except Exception:
            # Vendored version of requests is removed from botocore
            pass
