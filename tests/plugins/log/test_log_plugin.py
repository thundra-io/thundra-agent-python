import logging
from logging.config import fileConfig

from catchpoint.context.execution_context_manager import ExecutionContextManager
from catchpoint.plugins.log.catchpoint_log_handler import CatchpointLogHandler


def test_when_catchpoint_log_handler_is_not_added_to_logger(handler, mock_context, mock_event):
    _, handler = handler

    handler(mock_event, mock_context)
    execution_context = ExecutionContextManager.get()
    assert len(execution_context.logs) == 0


def test_log_plugin_with_initialization():
    logger = logging.getLogger('test_handler')
    log_handler = CatchpointLogHandler()
    logger.addHandler(log_handler)
    logger.setLevel(logging.INFO)
    execution_context = ExecutionContextManager.get()
    execution_context.capture_log = True
    logger.info("This is an info log")

    try:
        assert len(execution_context.logs) == 1
        log = execution_context.logs[0]

        assert log['logMessage'] == "This is an info log"
        assert log['logContextName'] == 'test_handler'
        assert log['logLevel'] == "INFO"
        assert log['logLevelCode'] == 2
    finally:
        del execution_context.logs[:]
        logger.removeHandler(log_handler)


def test_log_plugin_with_config_file():
    # config file path. Make sure path is correct with respect to where test is invoked
    fileConfig('tests/plugins/log/test_log_config.ini')
    logger = logging.getLogger('test_config_handler')
    execution_context = ExecutionContextManager.get()
    execution_context.capture_log = True
    logger.debug("This is a debug log")

    assert len(execution_context.logs) == 1
    log = execution_context.logs[0]

    assert log['logMessage'] == "This is a debug log"
    assert log['logContextName'] == 'test_config_handler'
    assert log['logLevel'] == "DEBUG"
    assert log['logLevelCode'] == 1
