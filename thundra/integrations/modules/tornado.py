import wrapt

from thundra import utils, constants
from thundra.config import config_names
from thundra.config.config_provider import ConfigProvider
from thundra.wrappers.tornado.middleware import ThundraMiddleware

def _wrapper(wrapped, instance, args, kwargs):
    try:
        # call middleware _execute, when tornado _execute called
        middleware = ThundraMiddleware(wrapped, instance)
        result = middleware._execute(args, kwargs)
    except:
        pass
    return result

def patch():
    if not ConfigProvider.get(config_names.THUNDRA_TRACE_INTEGRATIONS_TORNADO_DISABLE) and (
           not utils.get_env_variable(constants.AWS_LAMBDA_FUNCTION_NAME)):
        wrapt.wrap_function_wrapper(
            'tornado.web',
            'RequestHandler._execute',
            _wrapper
        )
