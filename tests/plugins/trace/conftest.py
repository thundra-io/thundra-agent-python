import pytest

from catchpoint.context.execution_context_manager import ExecutionContextManager
from catchpoint.opentracing.tracer import CatchpointTracer


@pytest.fixture(autouse=True)
def start_root_span():
    tracer = CatchpointTracer.get_instance()
    execution_context = ExecutionContextManager.get()
    tracer.start_active_span(operation_name="test",
                             finish_on_close=False,
                             trace_id="test-trace-id",
                             transaction_id="test-transaction-id",
                             execution_context=execution_context)


@pytest.fixture()
def empty_span_listener():
    return {
        "type": "FilteringSpanListener",
        "config": {
            "listener": {
                "type": "ErrorInjectorSpanListener",
                "config": {
                    "errorType": "NameError",
                    "errorMessage": "foo"
                }
            }
        }
    }


@pytest.fixture()
def span_listener_with_one_listener():
    return {
        "type": "FilteringSpanListener",
        "config": {
            "listener": {
                "type": "ErrorInjectorSpanListener",
                "config": {
                    "errorType": "NameError",
                    "errorMessage": "foo"
                }
            }
        }
    }


@pytest.fixture()
def span_listener_with_one_filterer():
    return {
        "type": "FilteringSpanListener",
        "config": {
            "filters": [
                {
                    "className": "AWS-SQS",
                    "domainName": "Messaging",
                    "tags": {
                        "foo": "bar"
                    }
                }
            ]
        }
    }


@pytest.fixture()
def span_listener_with_filterer_and_listener():
    return {
        "type": "FilteringSpanListener",
        "config": {
            "listener": {
                "type": "ErrorInjectorSpanListener",
                "config": {
                    "errorType": "NameError",
                    "errorMessage": "foo",
                    "injectOnFinish": True,
                    "injectCountFreq": 3
                }
            },
            "filters": [
                {
                    "className": "AWS-SQS",
                    "domainName": "Messaging",
                    "tags": {
                        "foo": "bar"
                    }
                }
            ]
        }
    }


@pytest.fixture()
def span_listener_with_multiple_filterers_and_listeners():
    return {
        "type": "FilteringSpanListener",
        "config": {
            "listener": {
                "type": "LatencyInjectorSpanListener",
                "config": {
                    "delay": 370,
                    "distribution": "normal",
                    "sigma": 73,
                    "variation": 37
                }
            },
            "filters": [
                {
                    "className": "AWS-SQS",
                    "domainName": "Messaging",
                    "tags": {
                        "foo": "bar"
                    }
                },
                {
                    "className": "HTTP",
                    "operationName": "http_request",
                    "tags": {
                        "http.host": "foobar.com"
                    }
                }
            ]
        }
    }
