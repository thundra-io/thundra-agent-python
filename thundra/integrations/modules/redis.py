import wrapt
from thundra import constants, config
from thundra.integrations.redis import RedisIntegration

redis_integration = RedisIntegration()
def _wrapper(wrapped, instance, args, kwargs):
    return redis_integration.run_and_trace(
        wrapped,
        instance,
        args,
        kwargs
    )

def patch():
    if not config.redis_integration_disabled():
        for method in map(str.lower, constants.RedisCommandTypes.keys()):
            try:
                wrapt.wrap_function_wrapper(
                    'redis.client',
                    'Redis.' + method,
                    _wrapper
                )
            except:
                pass
