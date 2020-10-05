import mock
import simplejson as json

from thundra import constants
from thundra.config import config_names
from thundra.config.config_provider import ConfigProvider
from thundra.reporter import Reporter


@mock.patch('thundra.reporter.requests')
def test_send_report_to_url(mock_requests, mock_report):
    ConfigProvider.set(config_names.THUNDRA_REPORT_REST_BASEURL, 'different_url/api')
    ConfigProvider.set(config_names.THUNDRA_REPORT_REST_COMPOSITE_ENABLE, 'false')
    test_session = mock_requests.Session()
    reporter = Reporter('api key', session=test_session)
    responses = reporter.send_reports([mock_report])

    post_url = 'different_url/api/monitoring-data'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'ApiKey api key'
    }

    reporter.session.post.assert_called_once_with(post_url, data=json.dumps([mock_report], separators=(',', ':')),
                                                  headers=headers, timeout=constants.DEFAULT_REPORT_TIMEOUT)
    reporter.session.post.return_value.status_code = 200
    for response in responses:
        assert response.status_code == 200


@mock.patch('thundra.reporter.requests')
def test_send_report_to_url_composite(mock_requests, mock_report, mock_invocation_report):
    ConfigProvider.set(config_names.THUNDRA_REPORT_REST_BASEURL, 'different_url/api')
    ConfigProvider.set(config_names.THUNDRA_REPORT_REST_COMPOSITE_ENABLE, 'true')
    ConfigProvider.set(config_names.THUNDRA_REPORT_REST_COMPOSITE_BATCH_SIZE, '1')

    test_session = mock_requests.Session()
    reporter = Reporter('api key', session=test_session)

    responses = reporter.send_reports([mock_invocation_report, mock_report])
    assert reporter.session.post.call_count == 2

    reporter.session.post.return_value.status_code = 200
    for response in responses:
        assert response.status_code == 200


@mock.patch('thundra.reporter.requests')
def test_send_report_to_url_async(mock_requests, mock_report):
    ConfigProvider.set(config_names.THUNDRA_REPORT_REST_BASEURL, 'different_url/api')
    ConfigProvider.set(config_names.THUNDRA_REPORT_CLOUDWATCH_ENABLE, 'true')

    test_session = mock_requests.Session()
    reporter = Reporter('api key', session=test_session)

    responses = reporter.send_reports([mock_report])

    reporter.session.post.assert_not_called()
    assert responses == []


@mock.patch('thundra.reporter.requests')
def test_send_report(mock_requests, mock_invocation_report):
    test_session = mock_requests.Session()
    reporter = Reporter('unauthorized api key', session=test_session)
    responses = reporter.send_reports([mock_invocation_report])

    assert reporter.session.post.call_count == 1
    test_session.post.return_value.status_code = 401
    for response in responses:
        assert response.status_code == 401


def test_get_report_batches(mock_report):
    ConfigProvider.set(config_names.THUNDRA_REPORT_REST_COMPOSITE_BATCH_SIZE, '2')

    reporter = Reporter('api key')
    batches = reporter.get_report_batches([mock_report] * 3)

    assert len(batches) == 2
    assert batches[0] == [mock_report, mock_report]
    assert batches[1] == [mock_report]


def test_prepare_report_json(mock_report, mock_report_with_byte_field):
    reporter = Reporter('api key')

    reports = reporter.prepare_report_json([mock_report, mock_report_with_byte_field])
    reports = json.loads(reports[0])

    assert len(reports) == 2
    assert reports[0].get('type') != 'bytes'
    assert reports[1].get('type') == 'bytes'


def test_prepare_report_json_batch(mock_report):
    ConfigProvider.set(config_names.THUNDRA_REPORT_REST_COMPOSITE_BATCH_SIZE, '1')

    reporter = Reporter('api key')

    batched_reports = reporter.prepare_report_json([mock_report] * 2)
    assert len(batched_reports) == 2

    reports = json.loads(batched_reports[0])
    assert len(reports) == 1


def test_prepare_composite_report_json(mock_report, mock_invocation_report):
    ConfigProvider.set(config_names.THUNDRA_REPORT_REST_COMPOSITE_BATCH_SIZE, '2')
    reporter = Reporter('api key')
    batched_reports = reporter.prepare_composite_report_json([mock_invocation_report, mock_report, mock_report])
    composite_report = json.loads(batched_reports[0])

    assert composite_report["type"] == "Composite"
    assert composite_report["apiKey"] == "api key"
    assert len(composite_report["data"]["allMonitoringData"]) == 2

    composite_report = json.loads(batched_reports[1])

    assert composite_report["type"] == "Composite"
    assert composite_report["apiKey"] == "api key"
    assert len(composite_report["data"]["allMonitoringData"]) == 1
