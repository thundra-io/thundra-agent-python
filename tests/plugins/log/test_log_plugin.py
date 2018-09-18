import logging
from logging.config import fileConfig

from thundra.plugins.log.thundra_log_handler import ThundraLogHandler, logs


def test_when_thundra_log_handler_is_not_added_to_logger(handler_with_apikey, mock_context, mock_event):
    thundra, handler = handler_with_apikey

    handler(mock_event, mock_context)
    assert len(logs) == 0


def test_log_plugin_with_initialization():

    logger = logging.getLogger('test_handler')
    log_handler = ThundraLogHandler()
    logger.addHandler(log_handler)
    logger.setLevel(logging.INFO)
    logger.info("This is an info log")

    assert len(logs) == 1
    log = logs[0]

    assert log['log'] == "This is an info log"
    assert log['logContextName'] == 'test_handler'              #Old: loggerName
    assert log['logLevel'] == "INFO"
    assert log['logLevelCode'] == 2                             #Old: loggerLevelId

    logs.clear()


def test_log_plugin_with_config_file():

    fileConfig('tests/plugins/log/test_log_config.ini')         # config file path. Make sure path is correct with respect to where test is invoked
    logger = logging.getLogger('test_config_handler')
    logger.debug("This is a debug log")

    assert len(logs) == 1
    log = logs[0]

    assert log['log'] == "This is a debug log"
    assert log['logContextName'] == 'test_config_handler'       #Old: loggerName
    assert log['logLevel'] == "DEBUG"
    assert log['logLevelCode'] == 1                             #Old: loggerLevelId
