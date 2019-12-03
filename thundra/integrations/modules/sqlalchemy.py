import wrapt
from thundra.integrations.sqlalchemy import SqlAlchemyIntegration
from thundra.config import utils as config_utils
from thundra import constants

def _wrapper(wrapped, instance, args, kwargs):
    engine = wrapped(*args, **kwargs)
    SqlAlchemyIntegration(engine)
    return engine


def patch():
    if not config_utils.get_bool_property(constants.THUNDRA_DISABLE_SQLALCHEMY_INTEGRATION):
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
