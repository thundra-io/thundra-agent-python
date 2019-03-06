import traceback
from thundra import config, constants
from thundra.plugins.invocation import invocation_support
from thundra.integrations.base_integration import BaseIntegration


op_types = {
    'PUT': 'WRITE',
    'POST': 'WRITE',
    'DELETE': 'DELETE',
}

class ElasticsearchIntegration(BaseIntegration):
    CLASS_TYPE = 'elasticsearch'

    def __init__(self):
        pass

    def get_host_and_port(self, instance):
        try:
            url = instance.connection_pool.connection.host
            host, port = url.rsplit(':', 1)
            return host, int(port)
        except (AttributeError, ValueError):
            return '', ''

    def get_operation_name(self, wrapped, instance, args, kwargs):
        try:
            es_uri = args[1]
            return es_uri
        except KeyError:
            return ''

    def before_call(self, scope, wrapped, instance, args, kwargs, response, exception):
        scope.span.class_name = constants.ClassNames['ELASTICSEARCH']
        scope.span.domain_name = constants.DomainNames['DB']

        host, port = self.get_host_and_port(instance)
        
        http_method, es_path = args
        es_body = kwargs.get('body', {})
        es_params = kwargs.get('params', {})
        operation_type = op_types.get(http_method, 'READ')

        tags = {
            constants.ESTags['ES_HOST']: host,
            constants.ESTags['ES_PORT']: port,
            constants.ESTags['ES_URI']: es_path,
            constants.ESTags['ES_METHOD']: http_method,
            constants.ESTags['ES_PARAMS']: es_params,
            constants.DBTags['DB_HOST']: host,
            constants.DBTags['DB_PORT']: port,
            constants.DBTags['DB_TYPE']: 'elasticsearch',
            constants.SpanTags['OPERATION_TYPE']: operation_type,
            constants.SpanTags['TRIGGER_OPERATION_NAMES']: [invocation_support.function_name],
            constants.SpanTags['TRIGGER_DOMAIN_NAME']: constants.LAMBDA_APPLICATION_DOMAIN_NAME,
            constants.SpanTags['TRIGGER_CLASS_NAME']: constants.LAMBDA_APPLICATION_CLASS_NAME,
            constants.SpanTags['TOPOLOGY_VERTEX']: True,
        }

        if not config.elasticsearch_body_masked():
            tags[constants.ESTags['ES_BODY']] = es_body

        scope.span.tags = tags

    def after_call(self, scope, wrapped, instance, args, kwargs, response, exception):
        host, port = self.get_host_and_port(instance)

        tags = {
            constants.ESTags['ES_HOST']: host,
            constants.ESTags['ES_PORT']: port,
            constants.DBTags['DB_HOST']: host,
            constants.DBTags['DB_PORT']: port,
        }

        scope.span.tags.update(tags)
        
        super().after_call(scope, wrapped, instance, args, kwargs, response, exception)
