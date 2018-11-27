from __future__ import absolute_import
import thundra.constants as Constants
from thundra.integrations.base_integration import BaseIntegrationFactory


class RedisIntegration():
    CLASS_TYPE = 'AWS'
    RESPONSE = {}
    OPERATION = {}

    def __init__(self):
        pass

    def getCommandType(self, string):
        if string in Constants.RedisCommandTypes:
            return Constants.RedisCommandTypes[string]
        return 'READ'

    # pylint: disable=W0613
    def inject_span_info(self, scope, wrapped, instance, args, kwargs, response,
                 exception):
        connection = str(instance.connection_pool).split(',')
        host = connection[0][connection[0].find('host=')+5:]
        port = connection[1][connection[1].find('port=')+5:]
        command_type = wrapped.__name__.upper()

        scope.span.domain_name = Constants.DomainNames['CACHE']
        scope.span.class_name = Constants.ClassNames['REDIS']
        scope.span.operation_name = 'REDIS | ' + self.getCommandType(command_type)
        scope.span.operationName = host

        ## ADDING TAGS ##

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
        }

        ## FINISHED ADDING TAGS ##
        scope.span.tags = tags


class RedisIntegrationFactory(object):

    @staticmethod
    def create_span(wrapped, instance, args, kwargs):
        integration_class = RedisIntegration
        return BaseIntegrationFactory().create_span(wrapped, instance, args, kwargs, 'redis_call', integration_class)