import wrapt
from thundra import utils, config
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
    if not config.http_integration_disabled():
        wrapt.wrap_function_wrapper(
            'requests',
            'Session.send',
            _wrapper
        )
        