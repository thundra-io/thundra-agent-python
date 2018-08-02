from multiprocessing.pool import ThreadPool
from threading import Thread

from thundra.opentracing.tracer import ThundraTracer
from thundra.plugins.trace.trace_aware_wrapper import TraceAwareWrapper
from thundra.plugins.trace.traceable import Traceable


def test_via_threadpool():
    numbers = [1, 2, 3, 4, 5]
    squared_numbers = calculate_parallel(numbers, 4)
    expected_result = [1,4,9,16,25]

    assert squared_numbers == expected_result

    tracer = ThundraTracer.getInstance()
    nodes = tracer.recorder.nodes
    active_span = None
    for key in nodes:
        if key.operation_name == 'calculate_parallel':
            active_span = key

    args = active_span.get_tag('ARGS')
    assert args[0]['argName'] == 'arg-0'
    assert args[0]['argValue'] == numbers
    assert args[0]['argType'] == 'list'
    assert args[1]['argName'] == 'arg-1'
    assert args[1]['argValue'] == 4
    assert args[1]['argType'] == 'int'

    return_value = active_span.get_tag('RETURN_VALUE')
    assert return_value['returnValue'] == squared_numbers
    assert return_value['returnValueType'] == 'list'

    error = active_span.get_tag('thrownError')
    assert error is None


def test_via_threading():
    numbers = [1, 2, 3, 4, 5]
    expected_result = [1, 4, 9, 16, 25]

    wrapper = TraceAwareWrapper()
    thread = Thread(target=wrapper(calculate_in_parallel), args=(numbers,))
    thread.start()
    thread.join()

    tracer = ThundraTracer.getInstance()
    nodes = tracer.recorder.nodes
    active_span = None
    for key in nodes:
        if key.operation_name == 'calculate_in_parallel':
            active_span = key

    args = active_span.get_tag('ARGS')
    assert args[0]['argName'] == 'arg-0'
    assert args[0]['argValue'] == numbers
    assert args[0]['argType'] == 'list'

    return_value = active_span.get_tag('RETURN_VALUE')
    assert return_value['returnValue'] == expected_result
    assert return_value['returnValueType'] == 'list'

    error = active_span.get_tag('thrownError')
    assert error is None


def square_number(n):
    return n ** 2

@Traceable(trace_args=True, trace_return_value=True)
def calculate_in_parallel(numbers):
    result = []
    for number in numbers:
        result.append(square_number(number))
    return result

@Traceable(trace_args=True, trace_return_value=True)
def calculate_parallel(numbers, threads=2):
    pool = ThreadPool(threads)
    wrapper = TraceAwareWrapper()
    result = pool.map(wrapper(square_number), numbers)
    pool.close()
    pool.join()
    return result