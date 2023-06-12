import catchpoint.constants as constants
from catchpoint.config import config_names
from catchpoint.config.config_provider import ConfigProvider
from catchpoint.integrations.base_integration import BaseIntegration
from catchpoint.integrations.rdb_base import RdbBaseIntegration


class DjangoORMIntegration(BaseIntegration, RdbBaseIntegration):
    CLASS_TYPE = 'django_orm'

    def __init__(self):
        pass

    def get_operation_name(self, wrapped, instance, args, kwargs):
        try:
            host = args[3]['cursor'].db.settings_dict.get('HOST')
        except:
            return ''
        return host

    def before_call(self, scope, execute, instance, _args, _kwargs, response, exception):
        scope.span.domain_name = constants.DomainNames['DB']
        scope.span.class_name = constants.ClassNames['RDB']

        try:
            db = _args[3]['cursor'].db
            settings = db.settings_dict
            vendor = db.vendor.upper()
            scope.span.class_name = constants.ClassNames.get(vendor, constants.ClassNames['RDB'])
        except:
            settings = {}
            vendor = ''

        query = ''
        operation = ''
        try:
            query = _args[0]
            if len(query) > 0:
                operation = query.split()[0].strip("\"").lower()
        except:
            pass

        tags = {
            constants.SpanTags['OPERATION_TYPE']: DjangoORMIntegration._OPERATION_TO_TYPE.get(operation, ''),
            constants.SpanTags['DB_INSTANCE']: settings.get('NAME'),
            constants.SpanTags['DB_HOST']: settings.get('HOST'),
            constants.SpanTags['DB_TYPE']: vendor,
            constants.SpanTags['DB_STATEMENT_TYPE']: operation.upper(),
            constants.SpanTags['TOPOLOGY_VERTEX']: True,
        }

        if not ConfigProvider.get(config_names.CATCHPOINT_TRACE_INTEGRATIONS_RDB_STATEMENT_MASK):
            tags[constants.DBTags['DB_STATEMENT']] = query

        scope.span.tags = tags
