import pytest
from thundra.listeners import AWSXRayListener


xray_listener = AWSXRayListener()

def test_normalize_operation_name():
    cases = [
        {
            'name': 'operation_name',
            'normalized_name': 'operation_name'
        },
        {
            'name': 'http://example.com',
            'normalized_name': 'http://example.com'
        },
        {
            'name': 'foo   bar',
            'normalized_name': 'foo bar'
        },
        {
            'name': 'foo\tbar',
            'normalized_name': 'foo bar'
        },
        {
            'name': 'a1 .:%&#=+\\-@',
            'normalized_name': 'a1 .:%&#=+\\-@'
        },
        {
            'name': 'operation_name?!',
            'normalized_name': 'operation_name'
        },
    ]

    for case in cases:
        assert case['normalized_name'] == xray_listener._normalize_operation_name(case['name'])

def test_add_annotations(mocked_subsegment, mocked_span):
    xray_listener._add_annotation(mocked_subsegment, mocked_span)
    annotations = mocked_subsegment.annotations

    assert annotations.get('traceId') == 'mocked_trace_id'
    assert annotations.get('transactionId') == 'mocked_transaction_id'
    assert annotations.get('spanId') == 'mocked_span_id'
    assert annotations.get('parentSpanId') == 'mocked_parent_span_id'
    assert annotations.get('duration') == 37
    assert annotations.get('domainName') == 'mocked_domain_name'
    assert annotations.get('className') == 'mocked_class_name'
    assert annotations.get('operationName') == 'mocked_operation_name'
    assert annotations.get('startTimeStamp') == 37
    assert annotations.get('finishTimeStamp') == 73