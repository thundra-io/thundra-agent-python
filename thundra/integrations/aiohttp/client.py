import aiohttp
import logging

from types import SimpleNamespace
from thundra.opentracing.tracer import ThundraTracer
from thundra.plugins.invocation import invocation_support
from thundra import constants, config, utils

logger = logging.getLogger(__name__)


async def on_request_start(session, trace_config_ctx, params):
    tracer = ThundraTracer.get_instance()
    if not tracer.get_active_span():
        return

    url_dict = utils.parse_http_url(str(params.url), config.http_integration_url_path_depth())
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
            constants.SpanTags['TRIGGER_OPERATION_NAMES']: [invocation_support.function_name],
            constants.SpanTags['TRIGGER_DOMAIN_NAME']: constants.LAMBDA_APPLICATION_DOMAIN_NAME,
            constants.SpanTags['TRIGGER_CLASS_NAME']: constants.LAMBDA_APPLICATION_CLASS_NAME,
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
    if not config.http_body_masked() and (scope.span.get_tag(constants.HttpTags["BODY"]) is None):
        body = params.chunk if params.chunk else ""
        scope.span.set_tag(constants.HttpTags["BODY"], body)


async def on_request_end(session, trace_config_ctx, params):
    if not hasattr(trace_config_ctx, "scope"):
        return
    scope = trace_config_ctx.scope

    response = params.response
    if response is not None:
        statusCode = response.status
        scope.span.set_tag(constants.HttpTags['HTTP_STATUS'], statusCode)

        if response.headers and (response.headers.get("x-amz-apigw-id") or response.headers.get("apigw-requestid")):
            scope.span.class_name = constants.ClassNames['APIGATEWAY']

        if response.headers and response.headers.get("x-thundra-resource-name"):
            resource_name = response.headers.get("x-thundra-resource-name")
            scope.span.operation_name = resource_name

        if (statusCode and config.http_error_status_code_min() <= statusCode):
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