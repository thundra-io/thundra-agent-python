import json
import mock
import asyncio
import asynctest
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
    responses = reporter.send_report()

    post_url = 'different_url/api/monitoring-data'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'ApiKey api key'
    }

    reporter.session.post.assert_called_once_with(post_url, data=json.dumps(reporter.reports), headers=headers)
    reporter.session.post.return_value.status_code = 200
    for response in responses:
        assert response.status_code == 200


@mock.patch('thundra.reporter.requests')
def test_send_report(mock_requests):
    test_session = mock_requests.Session()
    reporter = Reporter('unauthorized api key', session=test_session)
    responses = reporter.send_report()
    post_url = constants.HOST + constants.PATH
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'ApiKey unauthorized api key'
    }

    reporter.session.post.assert_called_once_with(post_url, data=json.dumps(reporter.reports), headers=headers)
    test_session.post.return_value.status_code = 401
    for response in responses:
        assert response.status_code == 401


def test_get_report_batches(mock_report, monkeypatch):
    constants.MAX_MONITOR_DATA_BATCH_SIZE=2

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

    dumped_reports = reporter.prepare_report_json(reporter.reports)
    reports = json.loads(dumped_reports)

    assert len(reports) == 1
    assert reports[0].get('type') != 'bytes'


@asynctest.patch('thundra.reporter.aiohttp.ClientSession.post')
def test_send_report_to_url_batch(mock_post, mock_report, monkeypatch):
    constants.MAX_MONITOR_DATA_BATCH_SIZE=1

    monkeypatch.setitem(os.environ, constants.THUNDRA_LAMBDA_REPORT_REST_BASEURL, 'different_url/api')
    reporter = Reporter('api key')
    reporter.add_report(mock_report)
    reporter.add_report(mock_report)

    mock_post.return_value.__aenter__.return_value = asynctest.MagicMock(status_code=200, read= asynctest.CoroutineMock())
    responses = reporter.send_report()

    post_url = 'different_url/api/monitoring-data'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'ApiKey api key'
    }

    assert mock_post.call_count == 2
    mock_post.assert_called_with(post_url, data=json.dumps([mock_report]), headers=headers)
    for response in responses:
        assert response.status_code == 200


@asynctest.patch('thundra.reporter.aiohttp.ClientSession.post')
def test_send_batch(mock_post, mock_report, monkeypatch):
    reporter = Reporter('api key')
    reporter.add_report(mock_report)
    mock_post.return_value.__aenter__.return_value = asynctest.MagicMock(status_code=200, read= asynctest.CoroutineMock())

    post_url = 'different_url/api/monitoring-data'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'ApiKey api key'
    }
    loop = asyncio.get_event_loop()
    response = loop.run_until_complete(reporter.send_batch(post_url, data=json.dumps([mock_report]), headers=headers))
    
    mock_post.assert_called_once_with(post_url, data=json.dumps([mock_report]), headers=headers)
    assert response.status_code == 200