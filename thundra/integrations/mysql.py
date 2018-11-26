from __future__ import absolute_import
import traceback
import thundra.constants as constants


class MysqlIntegration():

    _OPERATION_TO_TABLE_NAME_KEYWORD = {
        'select': 'from',
        'insert': 'into',
        'update': 'update',
        'delete': 'from',
        'create': 'table'
    }

    _OPERATION_TO_TYPE = {
        'select': 'READ',
        'insert': 'WRITE',
        'update': 'WRITE',
        'delete': 'DELETE'
    }

    def __init__(self):
        pass

    def inject_span_info(self, scope, cursor, connection, _args, _kwargs, response, exception):
        span = scope.span
        span.domain_name = constants.DomainNames['DB']
        span.class_name = constants.ClassNames['RDB']

        query = str(cursor.__self__._executed)[2:-1].lower()
        operation = query.split()[0].strip("\"").lower()
        tableName = self._extract_table_name(query, operation)

        print(operation)
        print(query)
        tags = {
            constants.SpanTags['SPAN_TYPE']: constants.SpanTypes['RDB'],
            constants.SpanTags['OPERATION_TYPE']: MysqlIntegration._OPERATION_TO_TYPE[operation],
            constants.SpanTags['DB_INSTANCE']: connection._database,
            constants.SpanTags['DB_URL']: connection._host,
            constants.SpanTags['DB_TYPE']: "mysql",
            constants.SpanTags['DB_STATEMENT']: query,
            constants.SpanTags['DB_STATEMENT_TYPE']: operation.upper(),
            constants.SpanTags['TRIGGER_DOMAIN_NAME']: "AWS-Lambda",
            constants.SpanTags['TRIGGER_CLASS_NAME']: "API"
        }

        span.tags = tags

        if exception is not None:
            self.set_exception(exception, traceback.format_exc(), span)

    def set_exception(self, exception, traceback_data, span):
        span.set_tag('error.stack', traceback_data)
        span.set_error_to_tag(exception)


    @staticmethod
    def _extract_table_name(query, operation):
        if operation in MysqlIntegration._OPERATION_TO_TABLE_NAME_KEYWORD:
            keyword = MysqlIntegration._OPERATION_TO_TABLE_NAME_KEYWORD[operation]
            query_words = query.lower().split()
            if keyword in query_words:
                return query.split()[query_words.index(keyword) + 1]
        return ''
