
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

    def set_exception(self, exception, traceback_data, span):
        span.set_tag('error.stack', traceback_data)
        span.set_error_to_tag(exception)