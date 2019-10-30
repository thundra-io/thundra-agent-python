import wrapt
import os
import thundra.integrations.botocore
from thundra import config
from thundra import constants
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

    return INTEGRATIONS['default'].run_and_trace(
            wrapped,
            instance,
            args,
            kwargs
        )  

def localstack_wrapper(wrapped, instance, args, kwargs):
    if 'LOCALSTACK_HOSTNAME' in os.environ:
        localstack_host = os.environ['LOCALSTACK_HOSTNAME']

        try:
            port = constants.LOCALSTACK_PORT_MAPPING.get(args[0])
            if port:
                kwargs["endpoint_url"] = "http://%s:%s" % (os.environ['LOCALSTACK_HOSTNAME'], port)
        except:
            pass

    return wrapped(*args, **kwargs)


def patch():
    if not config.aws_integration_disabled():
        wrapt.wrap_function_wrapper(
            'botocore.client',
            'BaseClient._make_api_call',
            _wrapper
        )
    if config.localstack_forwarding_enabled():
        wrapt.wrap_function_wrapper(
            'boto3.session',
            'Session.client',
            localstack_wrapper
        )

        wrapt.wrap_function_wrapper(
            'boto3.session',
            'Session.resource',
            localstack_wrapper
        )

    if not config.http_integration_disabled():
        try:
            wrapt.wrap_function_wrapper(
                'botocore.vendored.requests',
                'Session.send',
                request_wrapper
            )
        except Exception:
            # Vendored version of requests is removed from botocore
            pass
