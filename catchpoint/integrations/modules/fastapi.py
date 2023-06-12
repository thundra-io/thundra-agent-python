import wrapt

from catchpoint import utils, constants
from catchpoint.config import config_names
from catchpoint.config.config_provider import ConfigProvider

def _wrapper(wrapped, instance, args, kwargs):
    """Set middleware to trace Fast api. Fastapi has been built on starlett and pydantic frameworks.
    Request and response flow has been handled by starlette that is a lightweight ASGI framework. Fastapi 
    has an class called APIRouter that extends starlett Router class which is used to handle connections by starlette.
    The middleware should be an ASGI Middleware. Thus, the __call__(scope, receive, send) function should be implemented. 
    By default, starlette add two middleware except user defined middlewares which are ServerErrorMiddleware and ExceptionMiddleware. 
    Middleware list seems like [ServerErrorMiddleware, user_defined_middlewares, ExceptionMiddleware]. This list added in
    reversed order. Therefore, when we add our FastapiMiddleware to the zero index, it is placed top of middleware hierarchy.

    Args:
        wrapped (module): Wrapped module
        instance (function): Module enter point
        args (list): Wrapped function list of arguments
        kwargs (dict): Wrapped function key:value arguments
    """
    from fastapi.middleware import Middleware
    from catchpoint.wrappers.fastapi.middleware import CatchpointMiddleware
    from catchpoint.wrappers.fastapi.fastapi_wrapper import FastapiWrapper
    middlewares = kwargs.pop("middleware", [])
    middlewares.insert(0, Middleware(CatchpointMiddleware, wrapper=FastapiWrapper.get_instance()))
    kwargs.update({"middleware": middlewares})
    wrapped(*args, **kwargs)


def patch():
    if not ConfigProvider.get(config_names.CATCHPOINT_TRACE_INTEGRATIONS_FASTAPI_DISABLE) and \
        not utils.get_env_variable(constants.AWS_LAMBDA_FUNCTION_NAME):
        wrapt.wrap_function_wrapper(
            "fastapi.applications",
            "FastAPI.__init__",
            _wrapper
        )