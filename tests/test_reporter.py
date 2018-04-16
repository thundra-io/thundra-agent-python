import json
import mock
import pytest

from thundra import constants
from thundra.reporter import Reporter


def test_add_report_async(mock_report, environment_variables_with_enable_async_monitoring):
    e_v = environment_variables_with_enable_async_monitoring
    e_v.start()
    reporter = Reporter('api key')
    reporter.add_report(mock_report)
    assert len(reporter.reports) is 0
    e_v.stop()


def test_add_report_sync(mock_report, environment_variables_with_disable_async_monitoring):
    e_v = environment_variables_with_disable_async_monitoring
    e_v.start()
    reporter = Reporter('api key')
    reporter.add_report(mock_report)

    assert len(reporter.reports) > 0
    assert mock_report in reporter.reports

    e_v.stop()


def test_add_report_sync_if_env_var_is_not_set(mock_report):
    reporter = Reporter('api key')
    reporter.add_report(mock_report)

    assert len(reporter.reports) > 0
    assert mock_report in reporter.reports


@mock.patch('thundra.reporter.requests')
def test_send_report(mock_requests):
    reporter = Reporter('api key')
    response = reporter.send_report()
    post_url = constants.HOST + constants.PATH
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'ApiKey api key'
    }
    mock_requests.post.assert_called_once_with(post_url, data=json.dumps(reporter.reports), headers=headers)
    mock_requests.post.return_value.status_code = 200
    assert response.status_code == 200


@mock.patch('thundra.reporter.requests')
def test_send_report_without_apikey(mock_requests):
    with pytest.raises(Exception) as exc:
        reporter = Reporter(None)
        reporter.send_report()


@mock.patch('thundra.reporter.requests')
def test_send_report(mock_requests):
    reporter = Reporter('unauthorized api key')
    response = reporter.send_report()
    post_url = constants.HOST + constants.PATH
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'ApiKey unauthorized api key'
    }
    mock_requests.post.assert_called_once_with(post_url, data=json.dumps(reporter.reports), headers=headers)
    mock_requests.post.return_value.status_code = 401
    assert response.status_code == 401