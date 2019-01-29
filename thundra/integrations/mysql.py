from __future__ import absolute_import
import traceback
import thundra.constants as constants
from thundra.integrations.base_integration import BaseIntegration
from thundra.integrations.rdb_base import RdbBaseIntegration
from thundra.plugins.log.thundra_logger import debug_logger


class MysqlIntegration(BaseIntegration, RdbBaseIntegration):

    def __init__(self):
        pass

    def get_operation_name(self, wrapped, instance, args, kwargs):
        return instance.database

    def inject_span_info(self, scope, cursor, connection, _args, _kwargs, response, exception):
        try:
            span = scope.span
            span.domain_name = constants.DomainNames['DB']
            span.class_name = constants.ClassNames['MYSQL']

            query = ''
            operation = ''
            try:
                query = str(cursor.__self__._executed, encoding='utf-8').lower()
                if len(query) > 0:
                    operation = query.split()[0].strip("\"").lower()
            except Exception:
                pass

            tags = {
                constants.SpanTags['OPERATION_TYPE']: MysqlIntegration._OPERATION_TO_TYPE.get(operation, ''),
                constants.SpanTags['DB_INSTANCE']: connection._database,
                constants.SpanTags['DB_HOST']: connection._host,
                constants.SpanTags['DB_TYPE']: "mysql",
                constants.SpanTags['DB_STATEMENT']: query,
                constants.SpanTags['DB_STATEMENT_TYPE']: operation.upper(),
                constants.SpanTags['TRIGGER_DOMAIN_NAME']: "AWS-Lambda",
                constants.SpanTags['TRIGGER_CLASS_NAME']: "API",
                constants.SpanTags['TRIGGER_OPERATION_NAMES']: [scope.span.tracer.function_name],
                constants.SpanTags['TOPOLOGY_VERTEX']: True,
                constants.SpanTags['TRIGGER_DOMAIN_NAME']: constants.LAMBDA_APPLICATION_DOMAIN_NAME,
                constants.SpanTags['TRIGGER_CLASS_NAME']: constants.LAMBDA_APPLICATION_CLASS_NAME
            }

            span.tags = tags

            if exception is not None:
                self.set_exception(exception, traceback.format_exc(), span)
        except:
            debug_logger('Invalid query')
