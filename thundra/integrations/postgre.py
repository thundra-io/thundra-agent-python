from __future__ import absolute_import
import traceback
import thundra.constants as constants
from thundra.integrations.base_integration import BaseIntegration
from thundra.integrations.rdb_base import RdbBaseIntegration

try:
    from psycopg2.extensions import parse_dsn

except ImportError:
    def parse_dsn(dsn):
        return dict(
            attribute.split("=") for attribute in dsn.split()
            if "=" in attribute
        )

class PostgreIntegration(BaseIntegration, RdbBaseIntegration):

    def __init__(self):
        pass

    def get_operation_name(self):
        return "postgresql"

    def inject_span_info(self, scope, cursor, connection, _args, _kwargs, response, exception):
        span = scope.span
        span.domain_name = constants.DomainNames['DB']
        span.class_name = constants.ClassNames['RDB']

        dsn = parse_dsn(connection.dsn)
        query = str(cursor.__self__.query)[2:-1].lower()
        operation = query.split()[0].strip("\"").lower()
        tableName = self._extract_table_name(query, operation)

        tags = {
            constants.SpanTags['SPAN_TYPE']: constants.SpanTypes['RDB'],
            constants.SpanTags['OPERATION_TYPE']: PostgreIntegration._OPERATION_TO_TYPE[operation],
            constants.SpanTags['DB_INSTANCE']: dsn['dbname'],
            constants.SpanTags['DB_HOST']: dsn['host'],
            constants.SpanTags['DB_TABLE_NAME']: tableName,
            constants.SpanTags['DB_TYPE']: "postgresql",
            constants.SpanTags['DB_STATEMENT']: query,
            constants.SpanTags['DB_STATEMENT_TYPE']: operation.upper(),
            constants.SpanTags['TRIGGER_DOMAIN_NAME']: "AWS-Lambda",
            constants.SpanTags['TRIGGER_CLASS_NAME']: "API"
        }

        span.tags = tags

        if exception is not None:
            self.set_exception(exception, traceback.format_exc(), span)