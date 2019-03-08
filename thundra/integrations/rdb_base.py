
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
