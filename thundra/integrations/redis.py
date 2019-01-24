from __future__ import absolute_import
import thundra.constants as Constants
from thundra.integrations.base_integration import BaseIntegration
from thundra.plugins.log.thundra_logger import debug_logger


class RedisIntegration(BaseIntegration):
    CLASS_TYPE = 'redis'

    def __init__(self):
        pass

    def get_operation_name(self, wrapped, instance, args, kwargs):
        try:
            connection = str(instance.connection_pool).split(',')
            host = connection[0][connection[0].find('host=') + 5:]
            return host
        except:
            debug_logger('Invalid connection')

        return 'redis_call'

    def getCommandType(self, string):
        if string in Constants.RedisCommandTypes:
            return Constants.RedisCommandTypes[string]
        return 'READ'

    def before_call(self, scope, wrapped, instance, args, kwargs, response, exception):
        connection = str(instance.connection_pool).split(',')
        host = connection[0][connection[0].find('host=')+5:] or 'localhost'
        port = connection[1][connection[1].find('port=')+5:] or 6379
        command_type = wrapped.__name__.upper() or ""

        scope.span.domain_name = Constants.DomainNames['CACHE']
        scope.span.class_name = Constants.ClassNames['REDIS']

        tags = {
            Constants.SpanTags['SPAN_TYPE']: Constants.SpanTypes['REDIS'],
            Constants.SpanTags['OPERATION_TYPE']: self.getCommandType(command_type),
            Constants.DBTags['DB_INSTANCE']: host + ':' + port,
            Constants.DBTags['DB_STATEMENT']: {'command': command_type.lower(), 'args': [str(arg) for arg in args]},
            Constants.DBTags['DB_STATEMENT_TYPE']: self.getCommandType(command_type),
            Constants.DBTags['DB_TYPE']: 'redis',
            Constants.RedisTags['REDIS_HOST']: host + ':' + port,
            Constants.RedisTags['REDIS_COMMAND_TYPE']: command_type,
            Constants.RedisTags['REDIS_COMMAND_ARGS']: [str(arg) for arg in args],
            Constants.RedisTags['REDIS_COMMAND']: self.getCommandType(command_type),
            Constants.SpanTags['TRIGGER_OPERATION_NAMES']: [scope.span.tracer.function_name],
            Constants.SpanTags['TRIGGER_DOMAIN_NAME']: Constants.LAMBDA_APPLICATION_DOMAIN_NAME,
            Constants.SpanTags['TRIGGER_CLASS_NAME']: Constants.LAMBDA_APPLICATION_CLASS_NAME,
            Constants.SpanTags['TOPOLOGY_VERTEX']: True,
        }

        scope.span.tags = tags

    def after_call(self, scope, wrapped, instance, args, kwargs, response, exception):
        pass