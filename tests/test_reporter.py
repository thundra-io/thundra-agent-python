import json
import mock
import os

from thundra import constants
from thundra.reporter import Reporter

def test_add_report_async(mock_report, monkeypatch):
    monkeypatch.setitem(os.environ, constants.THUNDRA_LAMBDA_PUBLISH_CLOUDWATCH_ENABLE, 'true')
    reporter = Reporter('api key')
    reporter.add_report(mock_report)
    assert len(reporter.reports) is 0


def test_add_report_sync(mock_report, monkeypatch):
    monkeypatch.setitem(os.environ, constants.THUNDRA_LAMBDA_PUBLISH_CLOUDWATCH_ENABLE, 'false')
    reporter = Reporter('api key')
    reporter.add_report(mock_report)

    assert len(reporter.reports) > 0
    assert mock_report in reporter.reports


def test_add_report_sync_if_env_var_is_not_set(mock_report):
    reporter = Reporter('api key')
    reporter.add_report(mock_report)

    assert len(reporter.reports) > 0
    assert mock_report in reporter.reports


@mock.patch('thundra.reporter.requests')
def test_send_report_to_url(mock_requests, monkeypatch):
    monkeypatch.setitem(os.environ, constants.THUNDRA_LAMBDA_PUBLISH_REST_BASEURL, 'different_url/api')
    reporter = Reporter('api key')
    response = reporter.send_report(test_mode=True)

    post_url = 'different_url/api/monitor-datas'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'ApiKey api key'
    }
    s = mock_requests.Session()
    s.post.assert_called_once_with(post_url, data=json.dumps(reporter.reports), headers=headers)
    s.post.return_value.status_code = 200
    assert response.status_code == 200


@mock.patch('thundra.reporter.requests')
def test_send_report(mock_requests):
    reporter = Reporter('unauthorized api key')
    response = reporter.send_report(test_mode=True)
    post_url = constants.HOST + constants.PATH
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'ApiKey unauthorized api key'
    }
    s = mock_requests.Session()
    s.assert_called_once_with(post_url, data=json.dumps(reporter.reports), headers=headers)
    s.post.return_value.status_code = 401
    assert response.status_code == 401
