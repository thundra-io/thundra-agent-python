from __future__ import absolute_import
import thundra.constants as constants
from thundra.integrations.base_integration import BaseIntegration
from thundra.plugins.log.thundra_logger import debug_logger


class RedisIntegration(BaseIntegration):
    CLASS_TYPE = 'redis'

    def __init__(self):
        pass

    def get_operation_name(self, wrapped, instance, args, kwargs):
        connection_kwargs = instance.connection_pool.connection_kwargs
        return connection_kwargs.get('host', 'Redis')
        

    # pylint: disable=W0613
    def inject_span_info(self, scope, wrapped, instance, args, kwargs, response, exception):
        connection_kwargs = instance.connection_pool.connection_kwargs
        host = connection_kwargs.get('host', '')
        port = connection_kwargs.get('port', '6379')
        command_type = wrapped.__name__.upper() or ""
        operation_type = constants.RedisCommandTypes.get(command_type, '')

        command = '{} {}'.format(command_type, ' '.join([str(arg) for arg in args]))

        scope.span.domain_name = constants.DomainNames['CACHE']
        scope.span.class_name = constants.ClassNames['REDIS']

        ## ADDING TAGS ##

        tags = {
            constants.SpanTags['OPERATION_TYPE']: operation_type,
            constants.DBTags['DB_INSTANCE']: host,
            constants.DBTags['DB_STATEMENT']: command,
            constants.DBTags['DB_STATEMENT_TYPE']: operation_type,
            constants.DBTags['DB_TYPE']: 'redis',
            constants.RedisTags['REDIS_HOST']: host,
            constants.RedisTags['REDIS_COMMAND_TYPE']: command_type,
            constants.RedisTags['REDIS_COMMAND']: command,
            constants.SpanTags['TRIGGER_OPERATION_NAMES']: [scope.span.tracer.function_name],
            constants.SpanTags['TRIGGER_DOMAIN_NAME']: constants.LAMBDA_APPLICATION_DOMAIN_NAME,
            constants.SpanTags['TRIGGER_CLASS_NAME']: constants.LAMBDA_APPLICATION_CLASS_NAME,
            constants.SpanTags['TOPOLOGY_VERTEX']: True,
        }

        ## FINISHED ADDING TAGS ##
        scope.span.tags = tags