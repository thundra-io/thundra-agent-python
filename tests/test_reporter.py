import simplejson as json
import mock
import os

from thundra import constants
from thundra.reporter import Reporter

@mock.patch('thundra.reporter.requests')
def test_add_report(mock_requests, mock_report, monkeypatch):
    monkeypatch.setitem(os.environ, constants.THUNDRA_LAMBDA_REPORT_CLOUDWATCH_ENABLE, 'false')
    reporter = Reporter('api key', mock_requests.Session())
    reporter.add_report(mock_report)

    assert len(reporter.reports) > 0
    assert mock_report in reporter.reports


@mock.patch('thundra.reporter.requests')
def test_add_report_sync_if_env_var_is_not_set(mock_requests, mock_report):
    reporter = Reporter('api key', mock_requests.Session())
    reporter.add_report(mock_report)

    assert len(reporter.reports) > 0
    assert mock_report in reporter.reports


@mock.patch('thundra.reporter.requests')
def test_send_report_to_url(mock_requests, mock_report, monkeypatch):
    monkeypatch.setitem(os.environ, constants.THUNDRA_LAMBDA_REPORT_REST_BASEURL, 'different_url/api')
    monkeypatch.setitem(os.environ, constants.THUNDRA_LAMBDA_REPORT_REST_COMPOSITE_ENABLED, 'false')
    test_session = mock_requests.Session()
    reporter = Reporter('api key', session=test_session)
    reporter.add_report(mock_report)
    responses = reporter.send_report()

    post_url = 'different_url/api/monitoring-data'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'ApiKey api key'
    }

    reporter.session.post.assert_called_once_with(post_url, data=json.dumps([mock_report], separators=(',', ':')), headers=headers)
    reporter.session.post.return_value.status_code = 200
    for response in responses:
        assert response.status_code == 200


@mock.patch('thundra.reporter.requests')
def test_send_report_to_url_composite(mock_requests, mock_report, mock_invocation_report, monkeypatch):
    monkeypatch.setitem(os.environ, constants.THUNDRA_LAMBDA_REPORT_REST_COMPOSITE_ENABLED, 'true')
    monkeypatch.setitem(os.environ, constants.THUNDRA_LAMBDA_REPORT_REST_COMPOSITE_BATCH_SIZE, "1")
    monkeypatch.setitem(os.environ, constants.THUNDRA_LAMBDA_REPORT_REST_BASEURL, 'different_url/api')

    test_session = mock_requests.Session()
    reporter = Reporter('api key', session=test_session)
    reporter.add_report(mock_invocation_report)
    reporter.add_report(mock_report)

    responses = reporter.send_report()

    post_url = 'different_url/api/monitoring-data'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'ApiKey api key'
    }

    assert reporter.session.post.call_count == 2

    reporter.session.post.return_value.status_code = 200
    for response in responses:
        assert response.status_code == 200



@mock.patch('thundra.reporter.requests')
def test_send_report_to_url_async(mock_requests, mock_report, mock_invocation_report, monkeypatch):
    monkeypatch.setitem(os.environ, constants.THUNDRA_LAMBDA_REPORT_CLOUDWATCH_ENABLE, 'true')
    monkeypatch.setitem(os.environ, constants.THUNDRA_LAMBDA_REPORT_REST_BASEURL, 'different_url/api')

    test_session = mock_requests.Session()
    reporter = Reporter('api key', session=test_session)
    reporter.add_report(mock_report)

    responses = reporter.send_report()

    post_url = 'different_url/api/monitoring-data'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'ApiKey api key'
    }

    reporter.session.post.assert_not_called()
    assert responses == []


@mock.patch('thundra.reporter.requests')
def test_send_report(mock_requests, mock_report, mock_invocation_report, monkeypatch):
    test_session = mock_requests.Session()
    reporter = Reporter('unauthorized api key', session=test_session)
    reporter.add_report(mock_invocation_report)
    responses = reporter.send_report()
    post_url = constants.HOST + constants.COMPOSITE_DATA_PATH
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'ApiKey unauthorized api key'
    }

    assert reporter.session.post.call_count == 1
    test_session.post.return_value.status_code = 401
    for response in responses:
        assert response.status_code == 401


def test_get_report_batches(mock_report, monkeypatch):
    monkeypatch.setitem(os.environ, constants.THUNDRA_LAMBDA_REPORT_REST_COMPOSITE_BATCH_SIZE, "2")

    reporter = Reporter('api key')
    reporter.add_report(mock_report)
    reporter.add_report(mock_report)
    reporter.add_report(mock_report)
    
    batches = reporter.get_report_batches()

    assert len(batches) == 2
    assert batches[0] == [mock_report, mock_report]
    assert batches[1] == [mock_report]


def test_prepare_report_json(mock_report, mock_report_with_byte_field):
    reporter = Reporter('api key')
    reporter.add_report(mock_report)
    reporter.add_report(mock_report_with_byte_field)

    reports = reporter.prepare_report_json()
    reports = json.loads(reports[0])

    assert len(reports) == 2
    assert reports[0].get('type') != 'bytes'
    assert reports[1].get('type') == 'bytes'

def test_prepare_report_json_batch(mock_report, monkeypatch):
    monkeypatch.setitem(os.environ, constants.THUNDRA_LAMBDA_REPORT_REST_COMPOSITE_BATCH_SIZE, "1")
    reporter = Reporter('api key')
    reporter.add_report(mock_report)
    reporter.add_report(mock_report)

    batched_reports = reporter.prepare_report_json()
    assert len(batched_reports) == 2

    reports = json.loads(batched_reports[0])
    assert len(reports) == 1

def test_prepare_composite_report_json(mock_report, mock_invocation_report, monkeypatch):
    monkeypatch.setitem(os.environ, constants.THUNDRA_LAMBDA_REPORT_REST_COMPOSITE_BATCH_SIZE, "2")
    reporter = Reporter('api key')
    reporter.add_report(mock_invocation_report)
    reporter.add_report(mock_report)
    reporter.add_report(mock_report)

    batched_reports = reporter.prepare_composite_report_json()
    composite_report = json.loads(batched_reports[0])

    assert composite_report["type"] == "Composite"
    assert composite_report["apiKey"] == "api key"
    assert len(composite_report["data"]["allMonitoringData"]) == 2

    composite_report = json.loads(batched_reports[1])

    assert composite_report["type"] == "Composite"
    assert composite_report["apiKey"] == "api key"
    assert len(composite_report["data"]["allMonitoringData"]) == 1