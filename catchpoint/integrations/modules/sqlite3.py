import wrapt

from catchpoint.integrations.sqlite3 import SQLiteIntegration
from catchpoint.config import config_names
from catchpoint.config.config_provider import ConfigProvider

sqlite_integration = SQLiteIntegration()


class SqliteCursorWrapper(wrapt.ObjectProxy):

    def __init__(self, cursor, connection_wrapper):
        super(SqliteCursorWrapper, self).__init__(cursor)
        self._self_connection = connection_wrapper

    def execute(self, *args, **kwargs):
        return sqlite_integration.run_and_trace(
            self.__wrapped__.execute,
            self._self_connection,
            args,
            kwargs,
        )

    def __enter__(self):
        # raise appropriate error if api not supported (should reach the user)
        self.__wrapped__.__enter__
        return self


class SqliteConnectionWrapper(wrapt.ObjectProxy):
    db_name = None
    host = None

    def __init__(self, connection, db_name, host='localhost'):
        super(SqliteConnectionWrapper, self).__init__(connection)
        self.db_name = db_name
        self.host = host

    def cursor(self):
        cursor = self.__wrapped__.cursor()
        return SqliteCursorWrapper(cursor, self)

    def execute(self, *args, **kwargs):
        return self.cursor().execute(*args, **kwargs)


def _wrapper(wrapped, instance, args, kwargs):
    db_name = args[0] if args and len(args) > 0 else None
    connection = wrapped(*args, **kwargs)
    return SqliteConnectionWrapper(connection, db_name)


def patch():
    if not ConfigProvider.get(config_names.CATCHPOINT_TRACE_INTEGRATIONS_RDB_DISABLE):
        wrapt.wrap_function_wrapper(
            'sqlite3',
            'connect',
            _wrapper)
        wrapt.wrap_function_wrapper(
            'sqlite3.dbapi2',
            'connect',
            _wrapper)



