import wrapt
from thundra import utils
from thundra.integrations.requests import RequestsIntegration
from thundra.config import utils as config_utils
from thundra import constants

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
    if not config_utils.get_bool_property(constants.THUNDRA_DISABLE_HTTP_INTEGRATION):
        wrapt.wrap_function_wrapper(
            'requests',
            'Session.send',
            _wrapper
        )
