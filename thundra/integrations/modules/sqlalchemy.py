import wrapt

from thundra.config import config_names
from thundra.config.config_provider import ConfigProvider
from thundra.integrations.sqlalchemy import SqlAlchemyIntegration


def _wrapper(wrapped, instance, args, kwargs):
    engine = wrapped(*args, **kwargs)
    SqlAlchemyIntegration(engine)
    return engine


def patch():
    if not ConfigProvider.get(config_names.THUNDRA_TRACE_INTEGRATIONS_SQLALCHEMY_DISABLE):
        try:
            from sqlalchemy.event import listen
            from sqlalchemy.engine.interfaces import ExecutionContext
            wrapt.wrap_function_wrapper(
                'sqlalchemy',
                'create_engine',
                _wrapper
            )

            wrapt.wrap_function_wrapper(
                'sqlalchemy.engine',
                'create_engine',
                _wrapper
            )
        except:
            pass
