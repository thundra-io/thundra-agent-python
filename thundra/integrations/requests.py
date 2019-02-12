from __future__ import absolute_import
import traceback
import thundra.constants as constants
from urllib.parse import urlparse
from thundra.plugins.invocation import invocation_support
from thundra.integrations.base_integration import BaseIntegration


class RequestsIntegration(BaseIntegration):
    CLASS_TYPE = 'http'

    def __init__(self):
        pass

    def get_operation_name(self, wrapped, instance, args, kwargs):
        prepared_request = args[0]
        url = prepared_request.url
        return url
    
    def before_call(self, scope, wrapped, instance, args, kwargs, response, exception):
        prepared_request = args[0]
        method = prepared_request.method
        url = prepared_request.url
        path = ''
        query = ''
        host = ''
        try:
            parsed_url = urlparse(url)
            path = parsed_url.path
            query = parsed_url.query
            host = parsed_url.netloc
        except Exception:
            pass
        
        span = scope.span
        
        span.domain_name =  constants.DomainNames['API']
        span.class_name =  constants.ClassNames['HTTP']

        tags = {
            constants.SpanTags['OPERATION_TYPE']: method,
            constants.HttpTags['HTTP_METHOD']: method,
            constants.HttpTags['HTTP_URL']: url,
            constants.HttpTags['HTTP_PATH']: path,
            constants.HttpTags['HTTP_HOST']: host,
            constants.HttpTags['QUERY_PARAMS']: query,
            constants.SpanTags['TRIGGER_OPERATION_NAMES']: [invocation_support.function_name],
            constants.SpanTags['TRIGGER_DOMAIN_NAME']: constants.LAMBDA_APPLICATION_DOMAIN_NAME,
            constants.SpanTags['TRIGGER_CLASS_NAME']: constants.LAMBDA_APPLICATION_CLASS_NAME,
            constants.SpanTags['TOPOLOGY_VERTEX']: True,
        }

        span.tags = tags
    
    def after_call(self, scope, wrapped, instance, args, kwargs, response, exception):
        span = scope.span

        if exception is not None:
            self.set_exception(exception, traceback.format_exc(), span)

        if response is not None:
            self.set_response(response, span)

    def set_exception(self, exception, traceback_data, span):
        span.set_tag('error.stack', traceback_data)
        span.set_error_to_tag(exception)
    
    def set_response(self, response, span):
        statusCode = response.status_code
        span.set_tag(constants.HttpTags['HTTP_STATUS'], statusCode)
