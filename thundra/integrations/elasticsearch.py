import traceback
from thundra import config, constants
from thundra.plugins.invocation import invocation_support
from thundra.integrations.base_integration import BaseIntegration


class ElasticsearchIntegration(BaseIntegration):
    CLASS_TYPE = 'elasticsearch'

    def __init__(self):
        pass

    def get_hosts(self, instance):
        try:
            hosts = [con.host for con in instance.connection_pool.connections]
            return hosts
        except Exception:
            return []

    def get_normalized_path(self, es_uri):
        path_depth = config.elasticsearch_integration_path_depth()

        path_seperator_count = 0
        normalized_path = ''
        prev_c = ''
        for c in es_uri:
            if c == '/' and prev_c != '/':
                path_seperator_count += 1

            if path_seperator_count > path_depth:
                break

            normalized_path += c
            prev_c = c
        return normalized_path

    def get_operation_name(self, wrapped, instance, args, kwargs):
        try:
            es_uri = args[1]
            return self.get_normalized_path(es_uri)
        except KeyError:
            return ''

    def before_call(self, scope, wrapped, instance, args, kwargs, response, exception):
        scope.span.class_name = constants.ClassNames['ELASTICSEARCH']
        scope.span.domain_name = constants.DomainNames['DB']

        operation_name = self.get_operation_name(wrapped, instance, args, kwargs)
        hosts = self.get_hosts(instance)
        
        http_method, es_path = args
        es_body = kwargs.get('body', {})
        es_params = kwargs.get('params', {})

        tags = {
            constants.ESTags['ES_HOSTS']: hosts,
            constants.ESTags['ES_URI']: es_path,
            constants.ESTags['ES_NORMALIZED_URI']: operation_name,
            constants.ESTags['ES_METHOD']: http_method,
            constants.ESTags['ES_PARAMS']: es_params,
            constants.DBTags['DB_TYPE']: 'elasticsearch',
            constants.SpanTags['OPERATION_TYPE']: http_method,
            constants.SpanTags['TRIGGER_OPERATION_NAMES']: [invocation_support.function_name],
            constants.SpanTags['TRIGGER_DOMAIN_NAME']: constants.LAMBDA_APPLICATION_DOMAIN_NAME,
            constants.SpanTags['TRIGGER_CLASS_NAME']: constants.LAMBDA_APPLICATION_CLASS_NAME,
            constants.SpanTags['TOPOLOGY_VERTEX']: True,
        }

        if not config.elasticsearch_body_masked():
            tags[constants.ESTags['ES_BODY']] = es_body

        scope.span.tags = tags
