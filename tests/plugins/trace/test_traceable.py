from catchpoint.opentracing.tracer import CatchpointTracer


def test_trace_args(trace_args):
    tracer = CatchpointTracer.get_instance()
    nodes = tracer.get_spans()
    count=0
    for key in nodes:
        if key.operation_name == 'func_args':
            count += 1

    assert count == 0

    traceable_trace_args, func_args = trace_args
    func_args('arg1', arg2='arg2')

    active_span = None
    nodes = tracer.get_spans()
    for key in nodes:
        if key.operation_name == 'func_args':
            count += 1
            active_span = key

    args = active_span.get_tag('method.args')
    assert len(args) == 2
    assert args[0]['value'] == 'arg1'
    assert args[0]['name'] == 'arg-0'
    assert args[0]['type'] == 'str'
    assert args[1]['value'] == 'arg2'
    assert args[1]['name'] == 'arg2'
    assert args[1]['type'] == 'str'

    return_value = active_span.get_tag('method.return_value')
    assert return_value is None

    error = active_span.get_tag('error')
    assert error is None

    assert count == 1
    assert traceable_trace_args.trace_args is True
    assert traceable_trace_args.trace_return_value is False
    assert traceable_trace_args.trace_error is True


def test_trace_return_values(trace_return_val):
    tracer = CatchpointTracer.get_instance()
    nodes = tracer.get_spans()
    count = 0
    for key in nodes:
        if key.operation_name == 'func_return_val':
            count += 1

    assert count == 0

    traceable_trace_return_val, func_return_val = trace_return_val
    response = func_return_val()

    active_span = None
    nodes = tracer.get_spans()
    for key in nodes:
        if key.operation_name == 'func_return_val':
            count += 1
            active_span = key

    args = active_span.get_tag('method.args')
    assert args is None

    return_value = active_span.get_tag('method.return_value')
    assert return_value['type'] == type(response).__name__
    assert return_value['value'] == response

    error = active_span.get_tag('error')
    assert error is None

    assert count == 1
    assert traceable_trace_return_val.trace_args is False
    assert traceable_trace_return_val.trace_return_value is True
    assert traceable_trace_return_val.trace_error is True


def test_trace_error(trace_error):
    tracer = CatchpointTracer.get_instance()
    nodes = tracer.get_spans()
    count = 0
    for key in nodes:
        if key.operation_name == 'func_with_error':
            count += 1

    assert count == 0

    traceable, func_with_error = trace_error
    try:
        func_with_error()
    except:
        active_span = None
        nodes = tracer.get_spans()
        for key in nodes:
            if key.operation_name == 'func_with_error':
                count += 1
                active_span = key

        args = active_span.get_tag('method.args')
        assert args is None

        return_value = active_span.get_tag('method.return_value')
        assert return_value is None

        thrown_error = active_span.get_tag('error.kind')
        assert thrown_error == 'Exception'

        assert count == 1
        assert traceable.trace_args is False
        assert traceable.trace_return_value is False
        assert traceable.trace_error is True


def test_trace_with_default_configs(trace):
    tracer = CatchpointTracer.get_instance()
    nodes = tracer.get_spans()
    count = 0
    for key in nodes:
        if key.operation_name == 'func':
            count += 1

    assert count == 0

    traceable, func = trace
    func(arg='test')

    active_span = None
    nodes = tracer.get_spans()
    for key in nodes:
        if key.operation_name == 'func':
            count += 1
            active_span = key

    args = active_span.get_tag('method.args')
    assert args is None

    return_value = active_span.get_tag('method.return_value')
    assert return_value is None

    error = active_span.get_tag('error')
    assert error is None

    assert count == 1
    assert traceable.trace_args is False
    assert traceable.trace_return_value is False
    assert traceable.trace_error is True


