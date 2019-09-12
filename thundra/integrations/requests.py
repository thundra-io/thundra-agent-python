import traceback

from thundra.compat import urlparse

from thundra import config
import thundra.constants as constants
from thundra.plugins.invocation import invocation_support
from thundra.integrations.base_integration import BaseIntegration


class RequestsIntegration(BaseIntegration):
    CLASS_TYPE = 'http'

    def __init__(self):
        pass

    def get_operation_name(self, wrapped, instance, args, kwargs):
        prepared_request = args[0]
        url_dict = self._parse_http_url(prepared_request.url)
        return url_dict.get('operation_name')

    def _parse_http_url(self, url):
        url_dict = {
            'path': '',
            'query': '',
            'host': '',
            'url': url
        }
        try:
            parsed_url = urlparse(url)
            url_dict['path'] = parsed_url.path
            url_dict['query'] = parsed_url.query
            url_dict['host'] = parsed_url.netloc

            normalized_path = self.get_normalized_path(parsed_url.path)
            url_dict['operation_name'] = parsed_url.hostname + normalized_path

            url_dict['url'] = parsed_url.hostname + parsed_url.path
        except Exception:
            pass
        return url_dict

    def get_normalized_path(self, url_path):
        path_depth = config.http_integration_url_path_depth()

        path_seperator_count = 0
        normalized_path = ''
        prev_c = ''
        for c in url_path:
            if c == '/' and prev_c != '/':
                path_seperator_count += 1

            if path_seperator_count > path_depth:
                break

            normalized_path += c
            prev_c = c
        return normalized_path

    def before_call(self, scope, wrapped, instance, args, kwargs, response, exception):
        prepared_request = args[0]
        method = prepared_request.method

        url_dict = self._parse_http_url(prepared_request.url)
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
            constants.SpanTags['TRIGGER_OPERATION_NAMES']: [invocation_support.function_name],
            constants.SpanTags['TRIGGER_DOMAIN_NAME']: constants.LAMBDA_APPLICATION_DOMAIN_NAME,
            constants.SpanTags['TRIGGER_CLASS_NAME']: constants.LAMBDA_APPLICATION_CLASS_NAME,
            constants.SpanTags['TOPOLOGY_VERTEX']: True,
        }

        span.tags = tags

        if not config.http_body_masked():
            body = prepared_request.body if prepared_request.body else ""
            scope.span.set_tag(constants.HttpTags["BODY"], body)

        try:
            prepared_request.headers.update({'x-thundra-span-id': span.span_id})
            span.set_tag(constants.SpanTags['TRACE_LINKS'], [span.span_id])
        except Exception as e:
            pass

    def after_call(self, scope, wrapped, instance, args, kwargs, response, exception):
        super(RequestsIntegration, self).after_call(scope, wrapped, instance, args, kwargs, response, exception)

        if response is not None:
            self.set_response(response, scope.span)
            if response.headers and response.headers.get("x-amz-apigw-id"):
                scope.span.class_name = constants.ClassNames['APIGATEWAY']

            if response.headers and response.headers.get("x-thundra-resource-name"):
                resource_name = response.headers.get("x-thundra-resource-name")
                scope.span.operation_name = resource_name

            if (response.status_code and config.http_error_status_code_min() <= response.status_code):
                scope.span.set_tag('error.kind', "HttpError")
                scope.span.set_tag('error', True)
                scope.span.set_tag('error.message', response.reason)

    def set_response(self, response, span):
        statusCode = response.status_code
        span.set_tag(constants.HttpTags['HTTP_STATUS'], statusCode)
