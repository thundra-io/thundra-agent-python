import wrapt

from catchpoint.config import config_names
from catchpoint.config.config_provider import ConfigProvider


def _wrapper(wrapped, instance, args, kwargs):
    try:
        from catchpoint.integrations.aiohttp.client import CatchpointTraceConfig
        trace_configs = kwargs.get('trace_configs', [])
        trace_configs.append(CatchpointTraceConfig())
        kwargs['trace_configs'] = trace_configs
    except:
        pass
    wrapped(*args, **kwargs)


def patch():
    if not ConfigProvider.get(config_names.CATCHPOINT_TRACE_INTEGRATIONS_HTTP_DISABLE):
        try:
            import aiohttp
            wrapt.wrap_function_wrapper(
                'aiohttp',
                'ClientSession.__init__',
                _wrapper
            )
        except ImportError:
            pass
