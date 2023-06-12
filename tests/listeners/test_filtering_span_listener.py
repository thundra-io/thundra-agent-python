import mock
from catchpoint.listeners.catchpoint_span_filterer import StandardSpanFilterer, SimpleSpanFilter
from catchpoint.listeners import FilteringSpanListener, ErrorInjectorSpanListener, LatencyInjectorSpanListener

def test_creation():
    f1 = SimpleSpanFilter()
    f2 = SimpleSpanFilter()

    filterer = StandardSpanFilterer(span_filters=[f1, f2])

    delegated_listener = LatencyInjectorSpanListener(delay=370)
    
    fsl = FilteringSpanListener(listener=delegated_listener, filterer=filterer)

    assert fsl.listener is delegated_listener
    assert fsl.filterer is filterer


def test_when_filter_is_none(mocked_listener, mocked_span):
    fsl = FilteringSpanListener(listener=mocked_listener)

    fsl.on_span_started(mocked_span)
    fsl.on_span_finished(mocked_span)

    mocked_listener.on_span_started.assert_called_once_with(mocked_span)
    mocked_listener.on_span_finished.assert_called_once_with(mocked_span)

def test_filters_applied_properly(mocked_listener, mocked_span):
    mocked_f1 = mock.Mock(name='mocked_filter_f1')
    mocked_f2 = mock.Mock(name='mocked_filter_f2')

    filterer = StandardSpanFilterer(span_filters=[mocked_f1, mocked_f2])

    fsl = FilteringSpanListener(listener=mocked_listener, filterer=filterer)

    # Test when all filters return false
    mocked_f1.accept.return_value = False
    mocked_f2.accept.return_value = False
    fsl.on_span_started(mocked_span)
    mocked_listener.on_span_started.assert_not_called()
    
    # Test when all filters return true
    mocked_f1.accept.return_value = True
    mocked_f2.accept.return_value = True
    fsl.on_span_started(mocked_span)
    mocked_listener.on_span_started.assert_called_with(mocked_span)

    # Test when some of the filters return true
    mocked_f1.accept.return_value = True
    mocked_f2.accept.return_value = False
    fsl.on_span_started(mocked_span)
    mocked_listener.on_span_started.assert_called_with(mocked_span)


def test_create_from_config():
    config = {
        'listener': {
            "type": "ErrorInjectorSpanListener",
			"config": {
                "errorType": "NameError",
                "errorMessage": "You have a very funny name!",
                "injectOnFinish": True,
                "injectCountFreq": 3
			}
        },
        "filters": [
                    {
                        "className": "AWS-SQS",
                        "domainName": "Messaging",
                    },
                    {
                        "className": "HTTP",
                        "tags": {
                            "http.host": "foo.com"
                        }
                    }
                ]
    }

    fsl = FilteringSpanListener.from_config(config)

    assert type(fsl.listener) is ErrorInjectorSpanListener
    assert fsl.listener.error_type is NameError
    assert fsl.listener.error_message == 'You have a very funny name!'
    assert fsl.listener.inject_on_finish
    assert fsl.listener.inject_count_freq == 3
    
    assert len(fsl.filterer.span_filters) == 2
    
    f1 = fsl.filterer.span_filters[0]
    f2 = fsl.filterer.span_filters[1]

    assert f1.class_name == 'AWS-SQS'
    assert f1.domain_name == 'Messaging'
    
    assert f2.class_name == 'HTTP'
    assert f2.tags.get('http.host') == 'foo.com'

