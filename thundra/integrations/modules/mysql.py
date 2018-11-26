from __future__ import absolute_import
import wrapt

from thundra import utils, constants
from thundra.integrations.base_integration import BaseIntegrationFactory
from thundra.integrations.mysql import MysqlBaseIntegration


class CursorWrapper(wrapt.ObjectProxy):

    def __init__(self, cursor, connection_wrapper):
        super(CursorWrapper, self).__init__(cursor)
        self._self_connection = connection_wrapper

    # @property
    def connection_wrapper(self):
        return self._self_connection

    # NOTE: tracing other API calls currently not supported
    # (as 'executemany' and 'callproc')
    def execute(self, *args, **kwargs):
        response = BaseIntegrationFactory.wrap_with_trace(
            MysqlBaseIntegration,
            "mysql",
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

class ConnectionWrapper(wrapt.ObjectProxy):
    def cursor(self, *args, **kwargs):
        cursor = self.__wrapped__.cursor(*args, **kwargs)
        return CursorWrapper(cursor, self)

def _connect_wrapper(wrapped, instance, args, kwargs):
    connection = wrapped(*args, **kwargs)
    return ConnectionWrapper(connection)


def patch():
    disable_rdb_integration_by_env = utils.get_configuration(constants.THUNDRA_DISABLE_RDB_INTEGRATION)
    if not utils.should_disable(disable_rdb_integration_by_env):
        wrapt.wrap_function_wrapper(
            'mysql.connector',
            'connect',
            _connect_wrapper
        )