import wrapt

from thundra.config import config_names
from thundra.config.config_provider import ConfigProvider
from thundra.integrations.elasticsearch import ElasticsearchIntegration

es_integration = ElasticsearchIntegration()


def _wrapper(wrapped, instance, args, kwargs):
    return es_integration.run_and_trace(
        wrapped,
        instance,
        args,
        kwargs
    )


def patch():
    if not ConfigProvider.get(config_names.THUNDRA_TRACE_INTEGRATIONS_ES_DISABLE):
        wrapt.wrap_function_wrapper(
            'elasticsearch',
            'transport.Transport.perform_request',
            _wrapper
        )
