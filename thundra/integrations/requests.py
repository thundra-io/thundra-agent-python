from __future__ import absolute_import
import time
import traceback
import thundra.constants as constants
from urllib.parse import urlparse
from thundra.opentracing.tracer import ThundraTracer

class RequestsIntegration():
    def __init__(self):
        pass    
    
    def set_span_info(self, scope, wrapped, instance, args, kwargs, response, exception):
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

class RequestsIntegrationFactory(object):
    @staticmethod
    def create_span(wrapped, instance, args, kwargs):
        integration_class = RequestsIntegration

        response = None
        exception = None

        tracer = ThundraTracer.get_instance()
        with tracer.start_active_span(operation_name="http_call", finish_on_close=True) as scope:
            try:
                response = wrapped(*args, **kwargs)
                return response
            except Exception as operation_exception:
                exception = operation_exception
                scope.span.set_tag('error', exception)
                raise
            finally:
                try:
                    integration_class().set_span_info(
                        scope,
                        wrapped,
                        instance,
                        args,
                        kwargs,
                        response,
                        exception
                    )
                except Exception as instrumentation_exception:
                    error = {
                        'type': str(type(instrumentation_exception)),
                        'message': str(instrumentation_exception),
                        'traceback': traceback.format_exc(),
                        'time': time.time()
                    }
                    scope.span.set_tag('instrumentation_error', error)
