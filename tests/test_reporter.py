import json
import mock
import os

from thundra import constants
from thundra.reporter import Reporter


@mock.patch('thundra.reporter.requests')
def test_add_report_async(mock_requests, mock_report, monkeypatch):
    monkeypatch.setitem(os.environ, constants.THUNDRA_LAMBDA_REPORT_CLOUDWATCH_ENABLE, 'true')
    reporter = Reporter('api key', mock_requests.Session())
    reporter.add_report(mock_report)
    assert len(reporter.reports) is 0


@mock.patch('thundra.reporter.requests')
def test_add_report_sync(mock_requests, mock_report, monkeypatch):
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
def test_send_report_to_url(mock_requests, monkeypatch):
    monkeypatch.setitem(os.environ, constants.THUNDRA_LAMBDA_REPORT_REST_BASEURL, 'different_url/api')
    test_session = mock_requests.Session()
    reporter = Reporter('api key', session=test_session)
    response = reporter.send_report()

    post_url = 'different_url/api/monitoring-data'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'ApiKey api key'
    }

    reporter.session.post.assert_called_once_with(post_url, data=json.dumps(reporter.reports), headers=headers)
    reporter.session.post.return_value.status_code = 200
    assert response.status_code == 200


@mock.patch('thundra.reporter.requests')
def test_send_report(mock_requests):
    test_session = mock_requests.Session()
    reporter = Reporter('unauthorized api key', session=test_session)
    response = reporter.send_report()
    post_url = constants.HOST + constants.PATH
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'ApiKey unauthorized api key'
    }

    reporter.session.post.assert_called_once_with(post_url, data=json.dumps(reporter.reports), headers=headers)
    test_session.post.return_value.status_code = 401
    assert response.status_code == 401

def test_prepare_report_json(mock_report, mock_report_with_byte_field):
    reporter = Reporter('api key')
    reporter.add_report(mock_report)
    reporter.add_report(mock_report_with_byte_field)

    dumped_reports = reporter.prepare_report_json()
    reports = json.loads(dumped_reports)

    assert len(reports) == 1
    assert reports[0].get('type') != 'bytes'

