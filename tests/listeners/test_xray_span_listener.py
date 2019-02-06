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