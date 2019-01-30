from thundra.plugins.trace import trace_support
from thundra.listeners import *

def test_get_class_and_config_parts():
    def prepare_case(case):
        return {
            'val': case[0],
            'listener': case[1],
            'config': case[2],
        }

    cases = [
        ('dummy_listener[]','dummy_listener',''),
        ('dummy_listener[a=a,b=b,c=c]','dummy_listener','a=a,b=b,c=c'),
        ('dummy_listener[a=a, b=b, c=c]','dummy_listener','a=a, b=b, c=c'),
        ('dummy_listener[a=b.c,b=c.d,c=d.e.f]','dummy_listener','a=b.c,b=c.d,c=d.e.f'),
        ('dummy_listener_2[a=1,b=2,c=3]','dummy_listener_2','a=1,b=2,c=3'),
        ('dummy_listener[?!./+-,;:]','dummy_listener','?!./+-,;:'),
        ('dummy_listener[?!./+-,;:]','dummy_listener','?!./+-,;:'),
        ('foo[bar]', 'foo', 'bar'),
        ('37[73]', '37', '73'),
        ('[foo]', None, None),
        ('//73%37![==,==,==]', None, None),

    ] 

    for case in map(prepare_case, cases):
        listener, config = trace_support._get_class_and_config_parts(case['val'])
        assert listener == case['listener']
        assert config == case['config']

def test_get_sl_class():
    def prepare_case(case):
        return {
            'class_name': case[0],
            'class_type': case[1],
        }
    
    cases = [
        ('ErrorInjectorSpanListener', ErrorInjectorSpanListener),
        ('LatencyInjectorSpanListener', LatencyInjectorSpanListener),
        ('FilteringSpanListener', FilteringSpanListener),
        ('AWSXRayListener', AWSXRayListener),
        ('ThundraSpanListener', None),
        ('NonExistingListener', None),
    ] 

    for case in map(prepare_case, cases):
        sl_class = trace_support._get_sl_class(case['class_name'])
        assert sl_class == case['class_type']

def test_parse_config():
    cases = [
        {
            'config_str': '',
            'config': {}
        },
        {
            'config_str': 'foobar',
            'config': {}
        },
        {
            'config_str': 'a=1,b=',
            'config': {
                'a': '1',
                'b': '',
            }
        },
        {
            'config_str': 'a=1,b=2,c=3',
            'config': {
                'a': '1',
                'b': '2',
                'c': '3',
            }
        },
        {
            'config_str': 'listener=SampleListener, config.param1=val1, config.param2=val2',
            'config': {
                'listener': 'SampleListener',
                'config.param1': 'val1',
                'config.param2': 'val2',
            }
        },
        {
            'config_str': 'listener=boto3.exceptions.Boto3Error,foo_bar=foo-bar',
            'config': {
                'listener': 'boto3.exceptions.Boto3Error',
                'foo_bar': 'foo-bar',
            }
        },
        {
            'config_str': 'listener=boto3.exceptions.Boto3Error,foo_bar=foo-bar',
            'config': {
                'listener': 'boto3.exceptions.Boto3Error',
                'foo_bar': 'foo-bar',
            }
        },
    ]

    for case in cases:
        config = trace_support._parse_config(case['config_str'])
        assert config == case['config']
    

