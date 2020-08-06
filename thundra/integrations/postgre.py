from thundra import constants
from thundra.integrations.rdb_base import RdbBaseIntegration
from thundra.integrations.base_integration import BaseIntegration
from thundra.config.config_provider import ConfigProvider
from thundra.config import config_names

try:
    from psycopg2.extensions import parse_dsn
except ImportError:
    def parse_dsn(dsn):
        return dict(
            attribute.split("=") for attribute in dsn.split()
            if "=" in attribute
        )


class PostgreIntegration(BaseIntegration, RdbBaseIntegration):
    CLASS_TYPE = 'postgresql'
    
    def __init__(self):
        pass

    def get_operation_name(self, wrapped, instance, args, kwargs):
        return parse_dsn(instance.dsn).get('dbname', '')

    def before_call(self, scope, cursor, connection, _args, _kwargs, response, exception):
        span = scope.span
        span.domain_name = constants.DomainNames['DB']
        span.class_name = constants.ClassNames['POSTGRESQL']

        dsn = parse_dsn(connection.dsn)
        
        query = ''
        operation = ''
        try:
            query = _args[0]
            if len(query) > 0:
                operation = query.split()[0].strip("\"").lower()
        except Exception:
            pass

        tags = {
            constants.SpanTags['OPERATION_TYPE']: PostgreIntegration._OPERATION_TO_TYPE.get(operation, ''),
            constants.SpanTags['DB_INSTANCE']: dsn.get('dbname', ''),
            constants.SpanTags['DB_HOST']: dsn.get('host', ''),
            constants.SpanTags['DB_TYPE']: "postgresql",
            constants.SpanTags['DB_STATEMENT_TYPE']: operation.upper(),
            constants.SpanTags['TRIGGER_CLASS_NAME']: "API",
            constants.SpanTags['TOPOLOGY_VERTEX']: True
        }

        if not ConfigProvider.get(config_names.THUNDRA_TRACE_INTEGRATIONS_RDB_STATEMENT_MASK):
            tags[constants.DBTags['DB_STATEMENT']] = query

        span.tags = tags

