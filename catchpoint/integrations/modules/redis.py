import wrapt

from catchpoint import constants
from catchpoint.config import config_names
from catchpoint.config.config_provider import ConfigProvider
from catchpoint.integrations.redis import RedisIntegration

redis_integration = RedisIntegration()


def _wrapper(wrapped, instance, args, kwargs):
    return redis_integration.run_and_trace(
        wrapped,
        instance,
        args,
        kwargs
    )


def patch():
    if not ConfigProvider.get(config_names.CATCHPOINT_TRACE_INTEGRATIONS_REDIS_DISABLE):
        for method in map(str.lower, constants.RedisCommandTypes.keys()):
            try:
                wrapt.wrap_function_wrapper(
                    'redis.client',
                    'Redis.' + method,
                    _wrapper
                )
            except:
                pass
