import wrapt

from thundra.config import config_names
from thundra.config.config_provider import ConfigProvider


def _wrapper(wrapped, instance, args, kwargs):
    try:
        from thundra.integrations.aiohttp.client import ThundraTraceConfig
        trace_configs = kwargs.get('trace_configs', [])
        trace_configs.append(ThundraTraceConfig())
        kwargs['trace_configs'] = trace_configs
    except:
        pass
    wrapped(*args, **kwargs)


def patch():
    if not ConfigProvider.get(config_names.THUNDRA_TRACE_INTEGRATIONS_HTTP_DISABLE):
        try:
            import aiohttp
            wrapt.wrap_function_wrapper(
                'aiohttp',
                'ClientSession.__init__',
                _wrapper
            )
        except ImportError:
            pass
