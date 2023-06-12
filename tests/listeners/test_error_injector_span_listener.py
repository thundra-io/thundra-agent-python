from catchpoint.listeners import ErrorInjectorSpanListener
from catchpoint.listeners.error_injector_span_listener import default_error_message
from boto3.exceptions import Boto3Error
from redis import AuthenticationError

def test_frequency(mocked_span):
    esl = ErrorInjectorSpanListener(
        inject_count_freq=3
    )

    for i in range(10):
        esl.on_span_finished(mocked_span)

    assert esl._counter == 0

    err_count = 0
    for i in range(33):
        try:
            esl.on_span_started(mocked_span)
        except Exception:
            err_count += 1
            pass

    assert esl._counter == 33
    assert err_count == 11

def test_err_type_and_message(mocked_span):
    error_type = NameError
    error_message = "Your name is not good for this mission!"
    esl = ErrorInjectorSpanListener(
        error_type=error_type,
        error_message=error_message,
        inject_on_finish=False
    )

    error_on_started = None
    try:
        esl.on_span_started(mocked_span)
    except Exception as e:
        error_on_started = e
    
    assert error_on_started is not None
    assert type(error_on_started) is error_type
    assert str(error_on_started) == error_message

    error_on_finished = None
    try:
        esl.on_span_finished(mocked_span)
    except Exception as e:
        error_on_finished = e
    
    assert error_on_finished is None

def test_create_from_config():
    config = {
        'errorType': 'NameError',
        'errorMessage': '"You have a very funny name!"',
        'injectOnFinish': 'true',
        'injectCountFreq': '7',
        'foo': 'bar',
    }

    esl = ErrorInjectorSpanListener.from_config(config)

    assert esl.error_type is NameError
    assert esl.error_message == "You have a very funny name!"
    assert esl.inject_on_finish
    assert esl.inject_count_freq == 7

def test_custom_error_creation():
    config = {
        'errorType': 'boto3.exceptions.Boto3Error',
        'errorMessage': '"You have a very funny name!"',
        'injectOnFinish': 'true',
        'injectCountFreq': '7',
        'foo': 'bar',
    }

    esl = ErrorInjectorSpanListener.from_config(config)

    assert esl.error_type is Boto3Error
    assert esl.error_message == "You have a very funny name!"
    assert esl.inject_on_finish
    assert esl.inject_count_freq == 7

def test_with_empty_err_type_from_config():
    config = {
        'errorType': '',
        'errorMessage': 'dummy error',
    }

    esl = ErrorInjectorSpanListener.from_config(config)

    assert esl.error_type is Exception
    assert esl.error_message == config['errorMessage']

def test_with_no_existing_err_type():
    config = {
        'errorType': 'foo.bar.NonExistingError',
        'errorMessage': "this error shouldn\'t be raised"
    }

    esl = ErrorInjectorSpanListener.from_config(config)

    assert esl.error_type is Exception
    assert esl.error_message == config['errorMessage']

def test_create_from_config_with_type_errors():
    config = {
        'errorMessage': 37,
        'injectCountFreq': 'foo',
    }

    esl = ErrorInjectorSpanListener.from_config(config)

    assert esl.error_message == default_error_message
    assert esl.inject_count_freq == 1

def test_err_from_config_with_custom_error(mocked_span):
    config = {
        'errorType': 'redis.AuthenticationError',
        'errorMessage': '"can\'t authenticate with redis :("',
    }

    esl = ErrorInjectorSpanListener.from_config(config)

    error_on_started = None
    try:
        esl.on_span_started(mocked_span)
    except Exception as e:
        error_on_started = e
    
    assert error_on_started is not None
    assert type(error_on_started) is AuthenticationError
    assert str(error_on_started) == "can't authenticate with redis :("

    error_on_finished = None
    try:
        esl.on_span_finished(mocked_span)
    except Exception as e:
        error_on_finished = e
    
    assert error_on_finished is None

