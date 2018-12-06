
class RdbBaseIntegration():
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

    @staticmethod
    def _extract_table_name(query, operation):
        if operation in RdbBaseIntegration._OPERATION_TO_TABLE_NAME_KEYWORD:
            keyword =  RdbBaseIntegration._OPERATION_TO_TABLE_NAME_KEYWORD[operation]
            query_words = query.lower().split()
            if keyword in query_words:
                return query.split()[query_words.index(keyword) + 1]
        return ''

    def set_exception(self, exception, traceback_data, span):
        span.set_tag('error.stack', traceback_data)
        span.set_error_to_tag(exception)