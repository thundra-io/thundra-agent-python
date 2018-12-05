from __future__ import absolute_import

import wrapt

from thundra import utils, constants
from thundra.integrations.mysql import MysqlIntegration

mysql_integration = MysqlIntegration()

class MysqlCursorWrapper(wrapt.ObjectProxy):

    def __init__(self, cursor, connection_wrapper):
        super(MysqlCursorWrapper, self).__init__(cursor)
        self._self_connection = connection_wrapper

    def execute(self, *args, **kwargs):
        response = mysql_integration.create_span(
            self.__wrapped__.execute,
            self._self_connection,
            args,
            kwargs,
        )
        return response


    def __enter__(self):
        # raise appropriate error if api not supported (should reach the user)
        self.__wrapped__.__enter__  # pylint: disable=W0104
        return self

class MysqlConnectionWrapper(wrapt.ObjectProxy):
    def cursor(self, *args, **kwargs):
        cursor = self.__wrapped__.cursor(*args, **kwargs)
        return MysqlCursorWrapper(cursor, self)

def _wrapper(wrapped, instance, args, kwargs):
    connection = wrapped(*args, **kwargs)
    return MysqlConnectionWrapper(connection)


def patch():
    disable_rdb_integration_by_env = utils.get_configuration(constants.THUNDRA_DISABLE_RDB_INTEGRATION)
    if not utils.should_disable(disable_rdb_integration_by_env):
        wrapt.wrap_function_wrapper(
            'mysql.connector',
            'connect',
            _wrapper)