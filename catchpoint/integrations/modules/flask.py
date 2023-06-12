import wrapt

from catchpoint import utils, constants
from catchpoint.config import config_names
from catchpoint.config.config_provider import ConfigProvider
from catchpoint.wrappers.flask.middleware import CatchpointMiddleware


def _wrapper(wrapped, instance, args, kwargs):
    response = wrapped(*args, **kwargs)
    try:
        catchpoint_middleware = CatchpointMiddleware()
        catchpoint_middleware.set_app(instance)
    except:
        pass
    return response


def patch():
    if not ConfigProvider.get(config_names.CATCHPOINT_TRACE_INTEGRATIONS_FLASK_DISABLE) and (
            not utils.get_env_variable(constants.AWS_LAMBDA_FUNCTION_NAME)):
        wrapt.wrap_function_wrapper(
            'flask',
            'Flask.__init__',
            _wrapper
        )
