from __future__ import absolute_import


import thundra.constants as Constants
from ..base_integration import BaseIntegration


class RedisIntegration(BaseIntegration):
    """
    Represents redis event.
    """
    def getCommandType(self, string):
        if string in Constants.RedisCommandTypes:
            return Constants.RedisCommandTypes[string]
        return 'READ'

    CLASS_TYPE = 'AWS'
    RESPONSE = {}
    OPERATION = {}

    # pylint: disable=W0613
    def __init__(self, scope, wrapped, instance, args, kwargs, response,
                 exception):
        """
        Initialize.
        :param wrapped: wrapt's wrapped
        :param instance: wrapt's instance
        :param args: wrapt's args
        :param kwargs: wrapt's kwargs
        :param response: response data
        :param exception: Exception (if happened)
        """
        super(RedisIntegration, self).__init__()
        connection = str(instance.connection_pool).split(',')
        host = connection[0][connection[0].find('host=')+5:]
        port = connection[1][connection[1].find('port=')+5:]
        command_type = wrapped.__name__.upper()

        scope.span.domainName = Constants.DomainNames['CACHE']
        scope.span.className = Constants.ClassNames['REDIS']
        scope.span.operation_name = 'redis: ' + self.getCommandType(command_type)
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


class RedisEventListener(BaseIntegration):
    """
    Factory class, generates redis event.
    """

    LISTENERS = {
        class_obj.CLASS_TYPE: class_obj
        for class_obj in RedisIntegration.__subclasses__()
    }

    @staticmethod
    def create_event(scope, wrapped, instance, args, kwargs, response,
                     exception):

        event = RedisIntegration(
            scope,
            wrapped,
            instance,
            args,
            kwargs,
            response,
            exception
        )