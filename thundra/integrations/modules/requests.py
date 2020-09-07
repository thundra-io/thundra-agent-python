import wrapt

from thundra import utils
from thundra.config import config_names
from thundra.config.config_provider import ConfigProvider
from thundra.integrations.requests import RequestsIntegration

request_integration = RequestsIntegration()


def _wrapper(wrapped, instance, args, kwargs):
    prepared_request = args[0]

    if utils.is_excluded_url(prepared_request.url):
        return wrapped(*args, **kwargs)

    return request_integration.run_and_trace(
        wrapped,
        instance,
        args,
        kwargs,
    )


def patch():
    if not ConfigProvider.get(config_names.THUNDRA_TRACE_INTEGRATIONS_HTTP_DISABLE):
        wrapt.wrap_function_wrapper(
            'requests',
            'Session.send',
            _wrapper
        )
