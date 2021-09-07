from thundra.config.config_provider import ConfigProvider
from thundra.config import config_names
from thundra.foresight.environment.environment_info_support import EnvironmentSupport
from thundra.foresight.model.test_run_start import TestRunStart

import logging, socket, time
from uuid import uuid4

LOGGER = logging.getLogger(__name__)


def _current_milli_time():
    return round(time.time() * 1000)

class LogCaptureInfo:
    def __init__(self, captured_stdout_logs, captured_stderr_logs, set_log_sampler):
        self.captured_stdout_logs = captured_stdout_logs
        self.captured_stderr_logs = captured_stderr_logs
        self.set_log_sampler = set_log_sampler


class TestRunScope:
    
    def __init__(self, id=None, task_id = None, start_timestamp = None, 
        log_capture_info=None, context = None):

        self.id = id
        self.task_id = task_id
        self.start_timestamp = start_timestamp
        self.log_capture_info = log_capture_info
        self.context = context


class TestRunnerSupport:

    PROJECT_ID = ConfigProvider.get(config_names.THUNDRA_TEST_PROJECT_ID)
    STATUS_REPORT_FREQ_SECS = ConfigProvider.get(config_names.THUNDRA_TEST_STATUS_REPORT_FREQUENCY)
    LOG_ENABLE = ConfigProvider.get(config_names.THUNDRA_TEST_LOG_ENABLE)
    MAX_LOG_COUNT = ConfigProvider.get(config_names.THUNDRA_TEST_LOG_COUNT_MAX)
    MAX_SPAN_COUNT = ConfigProvider.get(config_names.THUNDRA_TEST_SPAN_COUNT_MAX)
    HOST_NAME = socket.gethostname()

    test_suite_contexts = dict()
    started_test_suites = set()
    test_run_scope = None


    @classmethod
    def on_test_suite_start(cls, test_module_name):
        cls.add_started_test_suite(test_module_name)


    @classmethod
    def add_started_test_suite(cls, test_module_name, thundra_span):
        if not test_module_name:
            return False
        cls.started_test_suites.add(test_module_name)
        return True


    @classmethod
    def on_test_suite_finish(cls, test_module_name):
        cls.remove_started_test_suite(test_module_name)
    

    @classmethod
    def remove_started_test_suite(cls, test_module_name):
        if not test_module_name:
            return False
        try:
            cls.started_test_suites.remove(test_module_name)
        except Exception as err:
            LOGGER.error("Started test suite with {} name couldn't be removed".format(test_module_name), err)
        return True


    @classmethod
    def clear_started_test_suites(cls):
        cls.started_test_suites.clear()


    @classmethod
    def start_test_suite_context(cls, test_suite_context):
        cls.test_suite_contexts[test_suite_context.transaction_id] = test_suite_context


    @classmethod
    def finish_test_suite_context(cls, test_suite_context):
        try:
            del cls.test_suite_contexts[test_suite_context.transaction_id]
        except Exception as err:
            LOGGER.error("Test suite couldn't removed from test suite contexts", err)


    @classmethod
    def clear_test_run(cls):
        test_run_scope = None


    @staticmethod
    def do_get_test_run_id():
        test_run_id = None
        environment_info = EnvironmentSupport.environment_info
        if not environment_info:
            test_run_id = environment_info.get_test_run_id()
        if not test_run_id:
            test_run_id = str(uuid4())
        return test_run_id

    
    @staticmethod
    def capture_logs():
        pass #TODO


    @staticmethod 
    def uncapture_logs():
        pass #TODO


    @classmethod
    def start_test_run(cls, context):
        id = cls.do_get_test_run_id()
        task_id = str(uuid4())
        current_time = _current_milli_time()
        logs = cls.capture_logs() #TODO
        test_run_scope = TestRunScope(id, task_id, current_time, logs, context)
        #TODO Sampling
        test_run_start = TestRunStart(
            test_run_scope.id,
            cls.PROJECT_ID,
            test_run_scope.task_id,
            test_run_scope.start_timestamp,
            cls.HOST_NAME,
            EnvironmentSupport.environment_info.environment
        )