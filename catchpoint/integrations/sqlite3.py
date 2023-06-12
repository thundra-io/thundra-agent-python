from catchpoint import constants
from catchpoint.config import config_names
from catchpoint.config.config_provider import ConfigProvider
from catchpoint.integrations.base_integration import BaseIntegration
from catchpoint.integrations.rdb_base import RdbBaseIntegration


class SQLiteIntegration(BaseIntegration, RdbBaseIntegration):
    CLASS_TYPE = 'sqlite'

    def __init__(self):
        super(SQLiteIntegration, self)

    def get_operation_name(self, wrapped, instance, args, kwargs):
        return instance.db_name

    def before_call(self, scope, cursor, connection, _args, _kwargs, response, exception):
        span = scope.span
        span.domain_name = constants.DomainNames['DB']
        span.class_name = constants.ClassNames['SQLITE']

        query = ''
        operation = ''
        try:
            query = _args[0]
            if len(query) > 0:
                operation = query.split()[0].strip("\"").lower()
        except Exception:
            pass

        tags = {
            constants.SpanTags['OPERATION_TYPE']: SQLiteIntegration._OPERATION_TO_TYPE.get(operation, ''),
            constants.SpanTags['DB_INSTANCE']: connection.db_name,
            constants.SpanTags['DB_HOST']: connection.host,
            constants.SpanTags['DB_TYPE']: self.CLASS_TYPE,
            constants.SpanTags['DB_STATEMENT_TYPE']: operation.upper(),
            constants.SpanTags['TOPOLOGY_VERTEX']: True,
        }

        if not ConfigProvider.get(config_names.CATCHPOINT_TRACE_INTEGRATIONS_RDB_STATEMENT_MASK):
            tags[constants.DBTags['DB_STATEMENT']] = query

        span.tags = tags
