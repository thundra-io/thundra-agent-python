import wrapt
from thundra import utils, config
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
    if not config.es_integration_disabled():
        wrapt.wrap_function_wrapper(
            'elasticsearch',
            'transport.Transport.perform_request',
            _wrapper
        )
