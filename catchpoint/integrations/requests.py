from opentracing import Format

import catchpoint.constants as constants
from catchpoint import utils
from catchpoint.opentracing.tracer import CatchpointTracer
from catchpoint.config import config_names
from catchpoint.config.config_provider import ConfigProvider
from catchpoint.integrations.base_integration import BaseIntegration


class RequestsIntegration(BaseIntegration):
    CLASS_TYPE = 'http'

    def __init__(self):
        pass

    def get_operation_name(self, wrapped, instance, args, kwargs):
        prepared_request = args[0]
        url_dict = utils.parse_http_url(prepared_request.url,
                                        ConfigProvider.get(config_names.CATCHPOINT_TRACE_INTEGRATIONS_HTTP_URL_DEPTH))
        return url_dict.get('operation_name')

    def before_call(self, scope, wrapped, instance, args, kwargs, response, exception):
        prepared_request = args[0]
        method = prepared_request.method

        url_dict = utils.parse_http_url(prepared_request.url,
                                        ConfigProvider.get(config_names.CATCHPOINT_TRACE_INTEGRATIONS_HTTP_URL_DEPTH))
        span = scope.span

        span.domain_name = constants.DomainNames['API']
        span.class_name = constants.ClassNames['HTTP']

        tags = {
            constants.SpanTags['OPERATION_TYPE']: method,
            constants.HttpTags['HTTP_METHOD']: method,
            constants.HttpTags['HTTP_URL']: url_dict.get('url'),
            constants.HttpTags['HTTP_PATH']: url_dict.get('path'),
            constants.HttpTags['HTTP_HOST']: url_dict.get('host'),
            constants.HttpTags['QUERY_PARAMS']: url_dict.get('query'),
            constants.SpanTags['TOPOLOGY_VERTEX']: True,
        }

        span.tags = tags

        if not ConfigProvider.get(config_names.CATCHPOINT_TRACE_INTEGRATIONS_HTTP_BODY_MASK):
            body = prepared_request.body if prepared_request.body else ""
            scope.span.set_tag(constants.HttpTags["BODY"], body)

        try:
            tracer = CatchpointTracer.get_instance()
            tracer.inject(span.context, Format.HTTP_HEADERS, prepared_request.headers)
            prepared_request.headers[constants.TRIGGER_RESOURCE_NAME_KEY] = url_dict.get('operation_name')

            span.set_tag(constants.SpanTags['TRACE_LINKS'], [span.span_id])
        except Exception as e:
            pass

    def after_call(self, scope, wrapped, instance, args, kwargs, response, exception):
        super(RequestsIntegration, self).after_call(scope, wrapped, instance, args, kwargs, response, exception)

        if response is not None:
            self.set_response(response, scope.span)
            if response.headers and (response.headers.get("x-amz-apigw-id") or response.headers.get("apigw-requestid")):
                scope.span.class_name = constants.ClassNames['APIGATEWAY']

            if response.headers and response.headers.get(constants.TRIGGER_RESOURCE_NAME_KEY):
                resource_name = response.headers.get(constants.TRIGGER_RESOURCE_NAME_KEY)
                scope.span.operation_name = resource_name

            if (response.status_code and \
                    ConfigProvider.get(
                        config_names.CATCHPOINT_TRACE_INTEGRATIONS_HTTP_ERROR_STATUS_CODE_MIN) <= response.status_code):
                scope.span.set_tag('error.kind', "HttpError")
                scope.span.set_tag('error', True)
                scope.span.set_tag('error.message', response.reason)

    def set_response(self, response, span):
        status_code = response.status_code
        span.set_tag(constants.HttpTags['HTTP_STATUS'], status_code)
