import pytest
import mock
from thundra import constants
from thundra.plugins.invocation import invocation_trace_support

tv = constants.SpanTags['TOPOLOGY_VERTEX']
ot = constants.SpanTags['OPERATION_TYPE']

@pytest.fixture
def mocked_span():
    def make_mocked_span(span_id='', class_name='', operation_name='', 
        operation_type='', topology_vertex=False,
        duration=0, errorneous=False, error_type=''):

        span = mock.Mock(name='mocked_span')
        span.span_id = span_id
        span.class_name = class_name
        span.operation_name = operation_name
        span.tags = {
            tv: topology_vertex, 
            ot: operation_type, 
            'error.kind': error_type
        }
        span.get_duration.return_value = duration
        span.errorneous.return_value = errorneous
        
        def get_tag(key):
            return span.tags.get(key)
        span.get_tag = get_tag

        return span
    return make_mocked_span

@mock.patch('thundra.opentracing.recorder.ThundraRecorder.get_spans')
def test_get_resources(mocked_get_spans, mocked_span):
    plugin_context = {
        'span_id': '0',
    }

    span_args = [
        {
            'id': '0',
            'cn': 'Class0',
            'on': 'operation0',
            'ot': 'type0',
            'd': 37,
            'tv': True,
            'e': False,
            'et': ''
        },
        {
            'id': '1',
            'cn': 'Class1',
            'on': 'operation1',
            'ot': 'type1',
            'd': 37,
            'tv': True,
            'e': True,
            'et': 'AnErrorType'
        },
        {
            'id': '2',
            'cn': 'Class1',
            'on': 'operation1',
            'ot': 'type1',
            'd': 73,
            'tv': True,
            'e': True,
            'et': 'AnotherErrorType'
        },
        {
            'id': '3',
            'cn': 'Class2',
            'on': 'operation2',
            'ot': 'type2',
            'd': 38,
            'tv': False,
            'e': False,
            'et': ''
        },
        {
            'id': '4',
            'cn': 'Class2',
            'on': 'operation2',
            'ot': 'type2',
            'd': 83,
            'tv': True,
            'e': True,
            'et': 'WeirdError'
        },
    ]
    spans = [
        mocked_span(span_id=args['id'], class_name=args['cn'], operation_name=args['on'],
            topology_vertex=args['tv'], operation_type=args['ot'], 
            errorneous=args['e'], error_type=args['et'],
            duration=args['d']) for args in span_args
    ]
    mocked_get_spans.return_value = spans

    resources = invocation_trace_support.get_resources(plugin_context)['resources']

    if resources[0]['resourceCount'] == 2:
        r1, r2 = resources[0], resources[1]
    else:
        r1, r2 = resources[1], resources[0]

    assert len(resources) == 2
    
    assert r1['resourceType'] == 'Class1'
    assert r1['resourceName'] == 'operation1'
    assert r1['resourceOperation'] == 'type1'
    assert r1['resourceCount'] == 2
    assert r1['resourceErrorCount'] == 2
    assert r1['resourceDuration'] == 110
    assert len(r1['resourceErrors']) == 2
    assert 'AnErrorType' in r1['resourceErrors']
    assert 'AnotherErrorType' in r1['resourceErrors']

    assert r2['resourceType'] == 'Class2'
    assert r2['resourceName'] == 'operation2'
    assert r2['resourceOperation'] == 'type2'
    assert r2['resourceCount'] == 1
    assert r2['resourceErrorCount'] == 1
    assert r2['resourceDuration'] == 83
    assert len(r2['resourceErrors']) == 1
    assert 'WeirdError' in r2['resourceErrors']
