import wrapt
from thundra import config
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


def patch():
    if not config.rdb_integration_disabled():
        wrapt.wrap_function_wrapper(
            'psycopg2',
            'connect',
            _wrapper)