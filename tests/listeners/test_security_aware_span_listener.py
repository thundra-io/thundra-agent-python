from catchpoint.listeners import SecurityAwareSpanListener
from catchpoint.opentracing.tracer import CatchpointTracer
from catchpoint import constants

def test_create_from_config():
    config = {
        'block': True,
        "blacklist": [
            {
                "className": "HTTP",
                "tags": {
                    "http.host": ["www.google.com", "www.yahoo.com"],
                    "operation.type": [
                        "GET",
                        "POST",
                        "PUT",
                    ]
                }
            },
            {
                "className": "AWS-DynamoDB",
                "tags": {
                    "aws.dynamodb.table.name": ["Users"],
                    "operation.type": [
                        "List",
                        "Read",
                        "Write",
                        "Tagging",
                        "PermissionsManagement"
                    ]
                }
            }
        ]
    }

    sasl = SecurityAwareSpanListener.from_config(config)

    assert sasl.block == True
    assert sasl.whitelist == None
    assert len(sasl.blacklist) == 2
    op1 = sasl.blacklist[0]
    assert op1.class_name == "HTTP"
    assert op1.tags == {"http.host": ["www.google.com", "www.yahoo.com"], 'operation.type': ['GET', 'POST', 'PUT']}


def test_violate():
    config = {
        'block': False,
        "blacklist": [
            {
                "className": "HTTP",
                "tags": {
                    "http.host": ["www.google.com", "www.yahoo.com"],
                    "operation.type": [
                        "GET",
                        "POST",
                        "PUT",
                    ]
                }
            },
            {
                "className": "AWS-DynamoDB",
                "tags": {
                    "aws.dynamodb.table.name": ["Users"],
                    "operation.type": [
                        "List",
                        "Read",
                        "Write",
                        "Tagging",
                        "PermissionsManagement"
                    ]
                }
            }
        ]  
    }

    sasl = SecurityAwareSpanListener.from_config(config)
    error_thrown = None

    tracer = CatchpointTracer.get_instance()
    span = tracer.create_span(operation_name='test')
    span.set_tag("http.host", "www.google.com")
    span.set_tag(constants.SpanTags['TOPOLOGY_VERTEX'], True)
    span.set_tag(constants.SpanTags['OPERATION_TYPE'], "GET")
    span.class_name = "HTTP"
    try:
        sasl.on_span_started(span)
    except Exception as e:
        error_thrown = e
    
    assert error_thrown == None
    assert span.get_tag(constants.SecurityTags["VIOLATED"]) == True


def test_block():
    config = {
        'block': True,
        "blacklist": [
            {
                "className": "HTTP",
                "tags": {
                    "http.host": ["www.google.com", "www.yahoo.com"],
                    "operation.type": [
                        "GET",
                        "POST",
                        "PUT",
                    ]
                }
            },
            {
                "className": "AWS-DynamoDB",
                "tags": {
                    "aws.dynamodb.table.name": ["Users"],
                    "operation.type": [
                        "List",
                        "Read",
                        "Write",
                        "Tagging",
                        "PermissionsManagement"
                    ]
                }
            }
        ]  
    }

    sasl = SecurityAwareSpanListener.from_config(config)
    error_thrown = None

    tracer = CatchpointTracer.get_instance()
    span = tracer.create_span(operation_name='test')
    span.set_tag("http.host", "www.google.com")
    span.set_tag(constants.SpanTags['TOPOLOGY_VERTEX'], True)
    span.set_tag(constants.SpanTags['OPERATION_TYPE'], "GET")
    span.class_name = "HTTP"
    try:
        sasl.on_span_started(span)
    except Exception as e:
        error_thrown = e
    
    assert str(error_thrown) == "Operation was blocked due to security configuration"
    assert span.get_tag(constants.SecurityTags["VIOLATED"]) == True
    assert span.get_tag(constants.SecurityTags["BLOCKED"]) == True


def test_whitelist():
    config = {
        'block': True,
        "whitelist": [
            {
                "className": "HTTP",
                "tags": {
                    "http.host": ["www.google.com", "www.yahoo.com"],
                    "operation.type": ["*"]
                }
            },
            {
                "className": "AWS-DynamoDB",
                "tags": {
                    "aws.dynamodb.table.name": ["Users"],
                    "operation.type": [
                        "List",
                        "Read",
                        "Write",
                        "Tagging",
                        "PermissionsManagement"
                    ]
                }
            }
        ]  
    }

    sasl = SecurityAwareSpanListener.from_config(config)
    error_thrown = None

    # Test whitelisted
    tracer = CatchpointTracer.get_instance()
    span = tracer.create_span(operation_name='test')
    span.set_tag("http.host", "www.google.com")
    span.set_tag(constants.SpanTags['TOPOLOGY_VERTEX'], True)
    span.set_tag(constants.SpanTags['OPERATION_TYPE'], "GET")
    span.class_name = "HTTP"
    try:
        sasl.on_span_started(span)
    except Exception as e:
        error_thrown = e
    
    assert error_thrown == None
    assert span.get_tag(constants.SecurityTags["VIOLATED"]) == None
    assert span.get_tag(constants.SecurityTags["BLOCKED"]) == None

    # Test span out of whitelist
    tracer = CatchpointTracer.get_instance()
    span = tracer.create_span(operation_name='test')
    span.set_tag("http.host", "www.test.com")
    span.set_tag(constants.SpanTags['TOPOLOGY_VERTEX'], True)
    span.set_tag(constants.SpanTags['OPERATION_TYPE'], "GET")
    span.class_name = "HTTP"
    try:
        sasl.on_span_started(span)
    except Exception as e:
        error_thrown = e
    
    assert str(error_thrown) == "Operation was blocked due to security configuration"
    assert span.get_tag(constants.SecurityTags["VIOLATED"]) == True
    assert span.get_tag(constants.SecurityTags["BLOCKED"]) == True


def test_operation_name():
    config = {
        'block': False,
        "blacklist": [
            {
                "className": "HTTP",
                "operationName": ["www.google.com/test"],
                "tags": {
                    "http.host": ["www.google.com"],
                    "operation.type": [
                        "GET",
                        "POST",
                        "PUT",
                    ]
                }
            }
        ]
    }

    sasl = SecurityAwareSpanListener.from_config(config)
    error_thrown = None

    tracer = CatchpointTracer.get_instance()
    span = tracer.create_span(operation_name='www.google.com/test')
    span.set_tag("http.host", "www.google.com")
    span.set_tag(constants.SpanTags['TOPOLOGY_VERTEX'], True)
    span.set_tag(constants.SpanTags['OPERATION_TYPE'], "GET")
    span.class_name = "HTTP"

    try:
        sasl.on_span_started(span)
    except Exception as e:
        error_thrown = e

    assert error_thrown == None
    assert span.get_tag(constants.SecurityTags["VIOLATED"]) == True