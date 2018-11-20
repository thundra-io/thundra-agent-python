from __future__ import absolute_import
import thundra.constants as constants
from thundra.utils import is_excluded_url
from urllib.parse import urlparse
from thundra.integrations.base_integration import BaseIntegration

class RequestEvent(BaseIntegration):
    """
    Represents requests library listener
    """
    CLASS_TYPE = 'requests'

    def __init__(self, scope, wrapped, instance, args, kwargs, response, exception):
        super(RequestEvent, self).__init__()
        
        prepared_request = args[0]

        method = prepared_request.method
        url = prepared_request.url
        parsed_url = urlparse(url)
        path = parsed_url.path
        query = parsed_url.query
        host = parsed_url.netloc
        statusCode = response.status_code
        
        scope.__getattribute__('_span').__setattr__('operation_name', url)
        scope.__getattribute__('_span').__setattr__('domain_name', constants.DomainNames['API'])
        scope.__getattribute__('_span').__setattr__('class_name', constants.ClassNames['HTTP'])

        ## ADDING TAGS ##

        tags = {
            constants.SpanTags['SPAN_TYPE']: constants.SpanTypes['HTTP'],
            constants.SpanTags['OPERATION_TYPE']: 'CALL',
            constants.HttpTags['HTTP_METHOD']: method,
            constants.HttpTags['HTTP_URL']: url,
            constants.HttpTags['HTTP_PATH']: path,
            constants.HttpTags['HTTP_HOST']: host,
            constants.HttpTags['QUERY_PARAMS']: query,
            constants.HttpTags['HTTP_STATUS']: statusCode
        }

        scope.__getattribute__('_span').__setattr__('tags', tags)

class RequestsEventFactory(object):
    @staticmethod
    def create_event(scope, wrapped, instance, args, kwargs, response, exception):
        requestObject = args[0]

        if is_excluded_url(requestObject.url):
            return

        instance_type = RequestEvent

        event = instance_type(
            scope,
            wrapped,
            instance,
            args,
            kwargs,
            response,
            exception
        )