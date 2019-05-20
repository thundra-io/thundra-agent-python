import wrapt
from thundra import utils, config
from thundra.integrations.sqlalchemy import SqlAlchemyIntegration


def _wrapper(wrapped, instance, args, kwargs):
    engine = wrapped(*args, **kwargs)
    SqlAlchemyIntegration(engine)
    return engine

def patch():
    if not config.sqlalchemy_integration_disabled():
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
