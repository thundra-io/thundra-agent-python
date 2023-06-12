import wrapt

from catchpoint import utils, constants
from catchpoint.config import config_names
from catchpoint.config.config_provider import ConfigProvider
from catchpoint.wrappers.tornado.middleware import CatchpointMiddleware


def _init_wrapper(_wrapped, _application, args, kwargs):
    _wrapped(*args, **kwargs)

    middleware = _application.settings.get('_catchpoint_middleware')
    if middleware is None:
        _application.settings['_catchpoint_middleware'] = CatchpointMiddleware()


async def _execute_wrapper(_wrapped, _handler, args, kwargs):
    middleware = _handler.settings.get('_catchpoint_middleware')
    middleware.execute(_handler)
    return await _wrapped(*args, **kwargs)


def _on_finish_wrapper(_wrapped, _handler, args, kwargs):
    middleware = _handler.settings.get('_catchpoint_middleware')
    middleware.finish(_handler)
    return _wrapped(*args, **kwargs)


def _log_exception_wrapper(_wrapped, _handler, args, kwargs):
    value = args[1] if len(args) == 3 else None
    if value is None:
        return _wrapped(*args, **kwargs)

    middleware = _handler.settings.get('_catchpoint_middleware')
    try:
        from tornado.web import HTTPError
        if not isinstance(value, HTTPError) or 500 <= value.status_code <= 599:
            middleware.finish(_handler, error=value)
    except ImportError:
        error = type('', (object,), {"status_code": 500})()
        middleware.finish(_handler, error=error)

    return _wrapped(*args, **kwargs)


def patch():
    if not ConfigProvider.get(config_names.CATCHPOINT_TRACE_INTEGRATIONS_TORNADO_DISABLE) and (
           not utils.get_env_variable(constants.AWS_LAMBDA_FUNCTION_NAME)):

        wrapt.wrap_function_wrapper(
            'tornado.web',
            'Application.__init__',
            _init_wrapper
        )
        wrapt.wrap_function_wrapper(
            'tornado.web',
            'RequestHandler._execute',
            _execute_wrapper
        )
        wrapt.wrap_function_wrapper(
            'tornado.web',
            'RequestHandler.on_finish',
            _on_finish_wrapper
        )
        wrapt.wrap_function_wrapper(
            'tornado.web',
            'RequestHandler.log_exception',
            _log_exception_wrapper
        )