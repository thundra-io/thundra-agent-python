from thundra import constants
from thundra.config import config_names
from thundra.config.config_provider import ConfigProvider
from thundra.integrations.base_integration import BaseIntegration
from thundra.integrations.rdb_base import RdbBaseIntegration


class MysqlIntegration(BaseIntegration, RdbBaseIntegration):
    CLASS_TYPE = 'mysql'

    def __init__(self):
        pass

    def get_operation_name(self, wrapped, instance, args, kwargs):
        return instance.database

    def before_call(self, scope, cursor, connection, _args, _kwargs, response, exception):
        span = scope.span
        span.domain_name = constants.DomainNames['DB']
        span.class_name = constants.ClassNames['MYSQL']

        query = ''
        operation = ''
        try:
            query = _args[0]
            if len(query) > 0:
                operation = query.split()[0].strip("\"").lower()
        except Exception:
            pass

        tags = {
            constants.SpanTags['OPERATION_TYPE']: MysqlIntegration._OPERATION_TO_TYPE.get(operation, ''),
            constants.SpanTags['DB_INSTANCE']: connection._database,
            constants.SpanTags['DB_HOST']: connection._host,
            constants.SpanTags['DB_TYPE']: "mysql",
            constants.SpanTags['DB_STATEMENT_TYPE']: operation.upper(),
            constants.SpanTags['TOPOLOGY_VERTEX']: True,
        }

        if not ConfigProvider.get(config_names.THUNDRA_TRACE_INTEGRATIONS_RDB_STATEMENT_MASK):
            tags[constants.DBTags['DB_STATEMENT']] = query

        span.tags = tags
