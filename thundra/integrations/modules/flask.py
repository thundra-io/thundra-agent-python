import wrapt

from thundra import utils, constants
from thundra.config import config_names
from thundra.config.config_provider import ConfigProvider
from thundra.wrappers.flask.middleware import ThundraMiddleware


def _wrapper(wrapped, instance, args, kwargs):
    response = wrapped(*args, **kwargs)
    try:
        thundra_middleware = ThundraMiddleware()
        thundra_middleware.set_app(instance)
    except:
        pass
    return response


def patch():
    if not ConfigProvider.get(config_names.THUNDRA_TRACE_INTEGRATIONS_FLASK_DISABLE) and (
            not utils.get_env_variable(constants.AWS_LAMBDA_FUNCTION_NAME)):
        wrapt.wrap_function_wrapper(
            'flask',
            'Flask.__init__',
            _wrapper
        )
