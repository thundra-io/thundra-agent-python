import logging
from types import SimpleNamespace

import aiohttp

from thundra import constants, utils
from thundra.config import config_names
from thundra.config.config_provider import ConfigProvider
from thundra.opentracing.tracer import ThundraTracer

logger = logging.getLogger(__name__)


async def on_request_start(session, trace_config_ctx, params):
    tracer = ThundraTracer.get_instance()
    if not tracer.get_active_span():
        return

    url_dict = utils.parse_http_url(str(params.url),
                                    ConfigProvider.get(config_names.THUNDRA_TRACE_INTEGRATIONS_HTTP_URL_DEPTH))
    scope = tracer.start_active_span(operation_name=url_dict.get('operation_name'), finish_on_close=False)
    scope.span.class_name = constants.ClassNames['HTTP']
    scope.span.domain_name = constants.DomainNames['API']

    tags = {
        constants.SpanTags['OPERATION_TYPE']: params.method,
        constants.HttpTags['HTTP_METHOD']: params.method,
        constants.HttpTags['HTTP_URL']: url_dict.get('url'),
        constants.HttpTags['HTTP_PATH']: url_dict.get('path'),
        constants.HttpTags['HTTP_HOST']: url_dict.get('host'),
        constants.HttpTags['QUERY_PARAMS']: url_dict.get('query'),
        constants.SpanTags['TOPOLOGY_VERTEX']: True,
    }

    scope.span.tags = tags
    try:
        scope.span.on_started()
        try:
            params.headers.update({'x-thundra-span-id': scope.span.span_id})
            scope.span.set_tag(constants.SpanTags['TRACE_LINKS'], [scope.span.span_id])
        except Exception as e:
            pass
        trace_config_ctx.scope = scope
    except Exception as e:
        logger.error(e)


async def on_request_chunk_sent(session, trace_config_ctx, params):
    if not hasattr(trace_config_ctx, "scope"):
        return
    scope = trace_config_ctx.scope
    if not ConfigProvider.get(config_names.THUNDRA_TRACE_INTEGRATIONS_HTTP_BODY_MASK) and \
            (scope.span.get_tag(constants.HttpTags["BODY"]) is None):
        body = params.chunk if params.chunk else ""
        scope.span.set_tag(constants.HttpTags["BODY"], body)


async def on_request_end(session, trace_config_ctx, params):
    if not hasattr(trace_config_ctx, "scope"):
        return
    scope = trace_config_ctx.scope

    response = params.response
    if response is not None:
        status_code = response.status
        scope.span.set_tag(constants.HttpTags['HTTP_STATUS'], status_code)

        if response.headers and (response.headers.get("x-amz-apigw-id") or response.headers.get("apigw-requestid")):
            scope.span.class_name = constants.ClassNames['APIGATEWAY']

        if response.headers and response.headers.get("x-thundra-resource-name"):
            resource_name = response.headers.get("x-thundra-resource-name")
            scope.span.operation_name = resource_name

        if (status_code and ConfigProvider.get(
                config_names.THUNDRA_TRACE_INTEGRATIONS_HTTP_ERROR_STATUS_CODE_MIN) <= status_code):
            scope.span.set_tag('error.kind', "HttpError")
            scope.span.set_tag('error', True)
            scope.span.set_tag('error.message', response.reason)
    try:
        scope.span.finish()
    except Exception as e:
        logger.error(e)

    scope.close()


async def on_request_exception(session, trace_config_ctx, params):
    if not hasattr(trace_config_ctx, "scope"):
        return
    scope = trace_config_ctx.scope
    scope.span.set_error_to_tag(params.exception)
    try:
        scope.span.finish()
    except Exception as e:
        logger.error(e)

    scope.close()


def ThundraTraceConfig():
    """
    :returns: TraceConfig.
    """

    def _trace_config_ctx_factory(trace_request_ctx):
        return SimpleNamespace(
            trace_request_ctx=trace_request_ctx
        )

    trace_config = aiohttp.TraceConfig(trace_config_ctx_factory=_trace_config_ctx_factory)
    trace_config.on_request_start.append(on_request_start)
    trace_config.on_request_end.append(on_request_end)
    trace_config.on_request_chunk_sent.append(on_request_chunk_sent)
    trace_config.on_request_exception.append(on_request_exception)
    return trace_config
