from __future__ import absolute_import
import traceback
import thundra.constants as constants
from urllib.parse import urlparse
from thundra.integrations.base_integration import BaseIntegration


class RequestsIntegration(BaseIntegration):
    CLASS_TYPE = 'http'

    def __init__(self):
        pass

    def get_operation_name(self):
        return 'http_call'
    
    def inject_span_info(self, scope, wrapped, instance, args, kwargs, response, exception):
        prepared_request = args[0]
        method = prepared_request.method
        url = prepared_request.url
        parsed_url = urlparse(url)
        path = parsed_url.path
        query = parsed_url.query
        host = parsed_url.netloc
        span = scope.span
        
        span.operation_name = url
        span.domain_name =  constants.DomainNames['API']
        span.class_name =  constants.ClassNames['HTTP']

        ## ADDING TAGS ##

        tags = {
            constants.SpanTags['SPAN_TYPE']: constants.SpanTypes['HTTP'],
            constants.SpanTags['OPERATION_TYPE']: 'CALL',
            constants.HttpTags['HTTP_METHOD']: method,
            constants.HttpTags['HTTP_URL']: url,
            constants.HttpTags['HTTP_PATH']: path,
            constants.HttpTags['HTTP_HOST']: host,
            constants.HttpTags['QUERY_PARAMS']: query,
        }

        span.tags = tags

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
