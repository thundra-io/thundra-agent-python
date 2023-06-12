import copy

import wrapt

from catchpoint.config import config_names
from catchpoint.config.config_provider import ConfigProvider
from catchpoint.integrations.postgre import PostgreIntegration

postgre_integration = PostgreIntegration()


class PostgreCursorWrapper(wrapt.ObjectProxy):

    def __init__(self, cursor, connection_wrapper):
        super(PostgreCursorWrapper, self).__init__(cursor)
        self._self_connection = connection_wrapper

    def execute(self, *args, **kwargs):
        return postgre_integration.run_and_trace(
            self.__wrapped__.execute,
            self._self_connection,
            args,
            kwargs,
        )

    def callproc(self, *args, **kwargs):
        return postgre_integration.run_and_trace(
            self.__wrapped__.callproc,
            self._self_connection,
            args,
            kwargs,
        )

    def __enter__(self):
        # raise appropriate error if api not supported (should reach the user)
        value = self.__wrapped__.__enter__()
        if value is not self.__wrapped__:
            return value
        return self


class PostgreConnectionWrapper(wrapt.ObjectProxy):
    def cursor(self, *args, **kwargs):
        cursor = self.__wrapped__.cursor(*args, **kwargs)
        return PostgreCursorWrapper(cursor, self)


def _wrapper(wrapped, instance, args, kwargs):
    connection = wrapped(*args, **kwargs)
    return PostgreConnectionWrapper(connection)


def _wrapper_register_type(wrapped, instance, args, kwargs):
    _args = list(copy.copy(args))
    if len(_args) == 2 and isinstance(_args[1], (PostgreConnectionWrapper, PostgreCursorWrapper)):
        _args[1] = _args[1].__wrapped__

    return wrapped(*_args, **kwargs)


def patch_extensions():
    _extensions = [
        ('psycopg2.extensions', 'register_type', _wrapper_register_type),
        ('psycopg2.extensions', 'quote_ident', _wrapper_register_type),
        ('psycopg2._psycopg', 'register_type', _wrapper_register_type)
    ]

    try:
        import psycopg2
        if getattr(psycopg2, '_json', None):
            _extensions.append(('psycopg2._json', 'register_type', _wrapper_register_type))
    except ImportError:
        pass

    for ext in _extensions:
        wrapt.wrap_function_wrapper(ext[0], ext[1], ext[2])


def patch():
    if not ConfigProvider.get(config_names.CATCHPOINT_TRACE_INTEGRATIONS_RDB_DISABLE):
        patch_extensions()
        wrapt.wrap_function_wrapper(
            'psycopg2',
            'connect',
            _wrapper)
