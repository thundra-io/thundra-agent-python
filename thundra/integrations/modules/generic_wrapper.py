"""
General wrapper for instrumentation.
"""

#pylint: disable=W0703
from __future__ import absolute_import
import time
import traceback
from thundra.opentracing.tracer import ThundraTracer


def wrapper(listener, wrapped, instance, args, kwargs):
    """
    General wrapper for instrumentation.
    :param factory: Factory class for the event type
    :param wrapped: wrapt's wrapped
    :param instance: wrapt's instance
    :param args: wrapt's args
    :param kwargs: wrapt's kwargs
    :return: None
    """

    response = None
    exception = None
    # start_time = time.time()

    tracer = ThundraTracer.get_instance()
    with tracer.start_active_span(operation_name="integration", finish_on_close=True) as scope:
        # scope.__setattr__('tags', {'idk': 'what is this'})
        # print(scope.__dict__['_span'].__dict__)
        # print("Printing scope: ", str(scope))
        try:
            response = wrapped(*args, **kwargs)
            return response
        except Exception as operation_exception:
            exception = operation_exception
            raise
        finally:
            try:
                listener.create_event(
                    scope,
                    wrapped,
                    instance,
                    args,
                    kwargs,
                    response,
                    exception
                )
            except Exception as instrumentation_exception:
                traceback.print_exc()
                print("Error in generic_wrapper")
                # tracer.add_exception(
                #     instrumentation_exception,
                #     traceback.format_exc()
                # )
