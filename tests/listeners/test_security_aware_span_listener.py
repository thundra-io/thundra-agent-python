import time
import mock
from thundra.listeners import SecurityAwareSpanListener
from thundra.opentracing.tracer import ThundraTracer
from thundra import constants

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
    assert sasl.whitelist == []
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

    tracer = ThundraTracer.get_instance()
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

    tracer = ThundraTracer.get_instance()
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
    tracer = ThundraTracer.get_instance()
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
    tracer = ThundraTracer.get_instance()
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
