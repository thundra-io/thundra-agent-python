import copy

import wrapt

from thundra.config import config_names
from thundra.config.config_provider import ConfigProvider
from thundra.integrations.postgre import PostgreIntegration

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
        self.__wrapped__.__enter__
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


def patch():
    if not ConfigProvider.get(config_names.THUNDRA_TRACE_INTEGRATIONS_RDB_DISABLE):
        wrapt.wrap_function_wrapper(
            'psycopg2.extensions',
            'register_type',
            _wrapper_register_type
        )

        wrapt.wrap_function_wrapper(
            'psycopg2',
            'connect',
            _wrapper)
