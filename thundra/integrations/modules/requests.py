from __future__ import absolute_import
import wrapt
from thundra import utils
from thundra import constants
from thundra.integrations.modules.generic_wrapper import wrapper
from thundra.integrations.requests import RequestsIntegrationFactory

def _wrapper(wrapped, instance, args, kwargs):
    prepared_request = args[0]

    if utils.is_excluded_url(prepared_request.url):
        return wrapped(*args, **kwargs)

    return wrapper(RequestsIntegrationFactory, wrapped, instance, args, kwargs)

def patch():
    disable_http_integration_by_env = utils.get_configuration(constants.THUNDRA_DISABLE_HTTP_INTEGRATION)
    if not utils.should_disable(disable_http_integration_by_env):
        wrapt.wrap_function_wrapper(
            'requests',
            'Session.send',
            _wrapper
        )
