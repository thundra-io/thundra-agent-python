import wrapt

from thundra import utils, constants
from thundra.config import config_names
from thundra.config.config_provider import ConfigProvider
from thundra.wrappers.tornado.middleware import ThundraMiddleware


def _init_wrapper(_wrapped, _application, args, kwargs):
    _wrapped(*args, **kwargs)

    middleware = _application.settings.get('_thundra_middleware')
    if middleware is None:
        _application.settings['_thundra_middleware'] = ThundraMiddleware()


async def _execute_wrapper(_wrapped, _handler, args, kwargs):
    middleware = _handler.settings.get('_thundra_middleware')
    middleware.execute(_handler)
    return await _wrapped(*args, **kwargs)


def _on_finish_wrapper(_wrapped, _handler, args, kwargs):
    middleware = _handler.settings.get('_thundra_middleware')
    middleware.finish(_handler)
    return _wrapped(*args, **kwargs)


def _log_exception_wrapper(_wrapped, _handler, args, kwargs):
    value = args[1] if len(args) == 3 else None
    if value is None:
        return _wrapped(*args, **kwargs)

    middleware = _handler.settings.get('_thundra_middleware')
    try:
        from tornado.web import HTTPError
        if not isinstance(value, HTTPError) or 500 <= value.status_code <= 599:
            middleware.finish(_handler, error=value)
    except ImportError:
        error = type('', (object,), {"status_code": 500})()
        middleware.finish(_handler, error=error)

    return _wrapped(*args, **kwargs)


def patch():
    if not ConfigProvider.get(config_names.THUNDRA_TRACE_INTEGRATIONS_TORNADO_DISABLE) and (
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