import wrapt

from thundra.config import config_names
from thundra.config.config_provider import ConfigProvider
from thundra.integrations.mysql import MysqlIntegration

mysql_integration = MysqlIntegration()


class MysqlCursorWrapper(wrapt.ObjectProxy):

    def __init__(self, cursor, connection_wrapper):
        super(MysqlCursorWrapper, self).__init__(cursor)
        self._self_connection = connection_wrapper

    def execute(self, *args, **kwargs):
        return mysql_integration.run_and_trace(
            self.__wrapped__.execute,
            self._self_connection,
            args,
            kwargs,
        )

    def callproc(self, *args, **kwargs):
        return mysql_integration.run_and_trace(
            self.__wrapped__.callproc,
            self._self_connection,
            args,
            kwargs,
        )

    def __enter__(self):
        # raise appropriate error if api not supported (should reach the user)
        self.__wrapped__.__enter__
        return self


class MysqlConnectionWrapper(wrapt.ObjectProxy):
    def cursor(self, *args, **kwargs):
        cursor = self.__wrapped__.cursor(*args, **kwargs)
        return MysqlCursorWrapper(cursor, self)


def _wrapper(wrapped, instance, args, kwargs):
    connection = wrapped(*args, **kwargs)
    return MysqlConnectionWrapper(connection)


def patch():
    if not ConfigProvider.get(config_names.THUNDRA_TRACE_INTEGRATIONS_RDB_DISABLE):
        wrapt.wrap_function_wrapper(
            'mysql.connector',
            'connect',
            _wrapper)
