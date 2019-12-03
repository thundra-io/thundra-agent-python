import wrapt
from thundra.integrations.elasticsearch import ElasticsearchIntegration
from thundra.config import utils as config_utils
from thundra import constants

es_integration = ElasticsearchIntegration()


def _wrapper(wrapped, instance, args, kwargs):
    return es_integration.run_and_trace(
        wrapped,
        instance,
        args,
        kwargs
    )


def patch():
    if not config_utils.get_bool_property(constants.THUNDRA_DISABLE_ES_INTEGRATION):
        wrapt.wrap_function_wrapper(
            'elasticsearch',
            'transport.Transport.perform_request',
            _wrapper
        )
