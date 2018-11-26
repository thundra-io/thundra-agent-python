from __future__ import absolute_import

import string

import thundra.constants as constants
from thundra.integrations.base_integration import BaseIntegration

try:
    from psycopg2.extensions import parse_dsn

except ImportError:
    def parse_dsn(dsn):
        return dict(
            attribute.split("=") for attribute in dsn.split()
            if "=" in attribute
        )

class DBIntegration(BaseIntegration):

    _OPERATION_TO_TABLE_NAME_KEYWORD = {
        'select': 'from',
        'insert': 'into',
        'update': 'update',
        'delete': 'from',
        'create': 'table'
    }

    _OPERATION_TO_TYPE = {
        'select': 'READ',
        'insert': 'COMMIT',
        'update': 'COMMIT',
        'delete': 'COMMIT',
        'create': 'COMMIT'
    }


    def __init__(self, scope, cursor, connection,_args, _kwargs, start_time, exception):

        super(DBIntegration, self).__init__()
        span = scope.span
        span.domain_name = constants.DomainNames['DB']
        span.class_name = constants.ClassNames['RDB']


        dsn = parse_dsn(connection.dsn)
        query = str(cursor.__self__.query)[2:-1].lower()
        operation = query.split()[0].lower().strip("\"")
        tableName =  self._extract_table_name(query, operation)

        tags = {
            constants.SpanTags['SPAN_TYPE']: constants.SpanTypes['RDB'],
            constants.SpanTags['OPERATION_TYPE']: DBIntegration._OPERATION_TO_TYPE[operation],
            constants.SpanTags['DB_INSTANCE']: dsn['dbname'],
            constants.SpanTags['DB_URL']: dsn['host'],
            constants.SpanTags['DB_TYPE']: "postgresql",
            constants.SpanTags['DB_STATEMENT']: query,
            constants.SpanTags['DB_STATEMENT_TYPE']: operation,
            constants.SpanTags['TRIGGER_DOMAIN_NAME']: "AWS-Lambda",
            constants.SpanTags['TRIGGER_CLASS_NAME']: "API"
        }

        span.tags = tags

    @staticmethod
    def _extract_table_name(query, operation):
        """
        Extract the table name from the SQL query string
        :param query: The SQL query string
        :param operation: The SQL operation used in the query
            (SELECT, INSERT, etc.)
        :return: Table name (string), "" if couldn't find
        """

        if operation in DBIntegration._OPERATION_TO_TABLE_NAME_KEYWORD:
            keyword = DBIntegration._OPERATION_TO_TABLE_NAME_KEYWORD[operation]
            query_words = query.lower().split()
            if keyword in query_words:
                return query.split()[query_words.index(keyword) + 1]
        return ''


class DBAPIEventListener(object):

    @staticmethod
    def create_event(scope, cursor_wrapper, instance, args, kwargs, response, exception):
        DBIntegration(
            scope,
            cursor_wrapper,
            instance,
            args,
            kwargs,
            response,
            exception,
        )



