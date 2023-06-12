from __future__ import absolute_import
import wrapt

from catchpoint import utils, constants
from catchpoint.config import config_names
from catchpoint.config.config_provider import ConfigProvider
from catchpoint.integrations.django import DjangoORMIntegration

try:
    from django.conf import settings
except ImportError:
    settings = None

CATCHPOINT_MIDDLEWARE = "catchpoint.wrappers.django.middleware.CatchpointMiddleware"

django_orm_integration = DjangoORMIntegration()


def _wrapper(wrapped, instance, args, kwargs):
    try:
        if getattr(settings, 'MIDDLEWARE', None):
            if CATCHPOINT_MIDDLEWARE in settings.MIDDLEWARE:
                return wrapped(*args, **kwargs)

            if isinstance(settings.MIDDLEWARE, tuple):
                settings.MIDDLEWARE = (CATCHPOINT_MIDDLEWARE,) + settings.MIDDLEWARE
            elif isinstance(settings.MIDDLEWARE, list):
                settings.MIDDLEWARE = [CATCHPOINT_MIDDLEWARE] + settings.MIDDLEWARE
        elif getattr(settings, 'MIDDLEWARE_CLASSES', None):
            if CATCHPOINT_MIDDLEWARE in settings.MIDDLEWARE_CLASSES:
                return wrapped(*args, **kwargs)

            if isinstance(settings.MIDDLEWARE_CLASSES, tuple):
                settings.MIDDLEWARE = (CATCHPOINT_MIDDLEWARE,) + settings.MIDDLEWARE_CLASSES
            elif isinstance(settings.MIDDLEWARE_CLASSES, list):
                settings.MIDDLEWARE = [CATCHPOINT_MIDDLEWARE] + settings.MIDDLEWARE_CLASSES

    except Exception:
        pass
    return wrapped(*args, **kwargs)


def db_execute_wrapper(execute, sql, params, many, context):
    return django_orm_integration.run_and_trace(
        execute,
        None,
        [sql,
         params,
         many,
         context],
        {}
    )


def install_db_execute_wrapper(connection, **kwargs):
    if db_execute_wrapper not in connection.execute_wrappers:
        connection.execute_wrappers.insert(0, db_execute_wrapper)


def patch():
    if not ConfigProvider.get(config_names.CATCHPOINT_TRACE_INTEGRATIONS_DJANGO_DISABLE) and (
            not utils.get_env_variable(constants.AWS_LAMBDA_FUNCTION_NAME)):
        wrapt.wrap_function_wrapper(
            'django.core.handlers.base',
            'BaseHandler.load_middleware',
            _wrapper
        )

    if not ConfigProvider.get(config_names.CATCHPOINT_TRACE_INTEGRATIONS_DJANGO_ORM_DISABLE):
        try:
            from django import VERSION
            from django.db import connections
            from django.db.backends.signals import connection_created

            if VERSION >= (2, 0):
                for connection in connections.all():
                    install_db_execute_wrapper(connection)

                connection_created.connect(install_db_execute_wrapper)
        except:
            pass
