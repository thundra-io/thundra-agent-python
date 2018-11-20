from __future__ import absolute_import
import thundra.constants as constants
from thundra.integrations.base_integration import BaseIntegration

class RequestEvent(BaseIntegration):
    """
    Represents requests library listener
    """
    CLASS_TYPE = 'requests'

    def __init__(self, scope, wrapped, instance, args, kwargs, response, exception):
        super(RequestEvent, self).__init__()
        
        requestObject = args[0]

        method = getattr(requestObject, 'method', 'GET')
        url = getattr(requestObject, 'url', '')
        path = requestObject.path_url
        queryParams = path.split('?')[1] if len(path.split('?')) > 1 else ''
        statusCode = response.status_code
        hwp = url[:-len(path):] # Host with protocol like http, https 
        host = hwp.split('//')[1] if len(hwp) > 1 else hwp
        
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
            constants.HttpTags['QUERY_PARAMS']: queryParams,
            constants.HttpTags['HTTP_STATUS']: statusCode
        }

        scope.__getattribute__('_span').__setattr__('tags', tags)

        if exception is not None:
            self.set_exception(exception)

class RequestsEventFactory(object):
    @staticmethod
    def create_event(wrapped, instance, args, kwargs, start_time, response, exception):
        instance_type = RequestEvent

        event = instance_type(
            wrapped,
            instance,
            args,
            kwargs,
            start_time,
            response,
            exception
        )