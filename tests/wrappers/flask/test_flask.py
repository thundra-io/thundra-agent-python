from unittest import mock

from flask import Flask, Blueprint

from catchpoint import constants
from catchpoint.context.execution_context_manager import ExecutionContextManager

app = Flask(__name__)
client = app.test_client()


@app.route('/')
def index():
    return 'hello'


@app.route('/error')
def error():
    raise RuntimeError('Test')


@mock.patch('catchpoint.wrappers.flask.flask_wrapper.FlaskWrapper.teardown_request')
@mock.patch('catchpoint.wrappers.flask.flask_wrapper.FlaskWrapper.after_request')
@mock.patch('catchpoint.wrappers.flask.flask_wrapper.FlaskWrapper.before_request')
def test_flask_hooks_called(mock_before_request, mock_after_request, mock_teardown_request):
    response = client.get('/')

    assert response.status_code == 200
    assert response.data == b'hello'

    assert mock_before_request.called
    assert mock_after_request.called
    assert mock_teardown_request.called


@mock.patch('catchpoint.wrappers.web_wrapper_utils.finish_trace')
def test_successful_view(finish_trace):
    response = client.get('/', query_string={'bar': 'baz'})
    execution_context = ExecutionContextManager.get()
    assert execution_context.root_span.operation_name == '/'
    assert execution_context.root_span.get_tag('http.method') == 'GET'
    assert execution_context.root_span.get_tag('http.host') == 'localhost'
    assert execution_context.root_span.get_tag('http.query_params') == b'bar=baz'
    assert execution_context.root_span.get_tag('http.path') == '/'
    assert execution_context.root_span.class_name == constants.ClassNames['FLASK']
    assert execution_context.root_span.domain_name == 'API'

    assert execution_context.tags.get(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == ['localhost/']
    assert execution_context.tags.get(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == 'API'
    assert execution_context.tags.get(constants.SpanTags['TRIGGER_CLASS_NAME']) == 'HTTP'
    assert execution_context.response.data == response.data
    assert execution_context.response.status_code == 200
    ExecutionContextManager.clear()


@mock.patch('catchpoint.wrappers.web_wrapper_utils.finish_trace')
def test_erroneous_view(finish_trace):
    client.get('/error', query_string={'bar': 'baz'})
    execution_context = ExecutionContextManager.get()
    assert execution_context.root_span.operation_name == '/error'
    assert execution_context.root_span.get_tag('http.method') == 'GET'
    assert execution_context.root_span.get_tag('http.host') == 'localhost'
    assert execution_context.root_span.get_tag('http.query_params') == b'bar=baz'
    assert execution_context.root_span.get_tag('http.path') == '/error'
    assert execution_context.root_span.class_name == constants.ClassNames['FLASK']
    assert execution_context.root_span.domain_name == 'API'

    assert execution_context.tags.get(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == ['localhost/error']
    assert execution_context.tags.get(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == 'API'
    assert execution_context.tags.get(constants.SpanTags['TRIGGER_CLASS_NAME']) == 'HTTP'
    assert execution_context.error is not None
    assert execution_context.response.status_code == 500
    ExecutionContextManager.clear()


@mock.patch('catchpoint.wrappers.web_wrapper_utils.finish_trace')
def test_blueprint(finish_trace):
    blueprint = Blueprint('test', __name__)

    @blueprint.route('/api/test', methods=('GET',))
    def test():
        return 'test'

    app.register_blueprint(blueprint)
    response = client.get('/api/test')
    execution_context = ExecutionContextManager.get()
    assert execution_context.root_span.operation_name == '/api/test'
    assert execution_context.root_span.get_tag('http.method') == 'GET'
    assert execution_context.root_span.get_tag('http.host') == 'localhost'
    assert execution_context.root_span.get_tag('http.path') == '/api/test'
    assert execution_context.root_span.class_name == constants.ClassNames['FLASK']
    assert execution_context.root_span.domain_name == 'API'

    assert execution_context.tags.get(constants.SpanTags['TRIGGER_OPERATION_NAMES']) == ['localhost/api/test']
    assert execution_context.tags.get(constants.SpanTags['TRIGGER_DOMAIN_NAME']) == 'API'
    assert execution_context.tags.get(constants.SpanTags['TRIGGER_CLASS_NAME']) == 'HTTP'
    assert execution_context.response.data == response.data
    assert execution_context.response.status_code == 200
    ExecutionContextManager.clear()
