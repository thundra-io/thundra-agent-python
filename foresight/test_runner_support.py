from thundra.config.config_provider import ConfigProvider
from thundra.config import config_names
from foresight.environment.environment_info_support import EnvironmentSupport
from foresight.model import (TestRunStart , TestRunStatus, TestRunResult, 
                                TestRunFinish, TestRunContext)
from foresight.utils.test_wrapper import TestWrapper
import foresight.utils.generic_utils as utils
import logging, socket, threading

LOGGER = logging.getLogger(__name__)

class _TestRunScope:
    
    def __init__(self, id=None, task_id = None, start_timestamp = None, context = None):

        self.id = id
        self.task_id = task_id
        self.start_timestamp = start_timestamp
        self.context = context

class _StatusReporter:

    def __init__(self):
        self.delay = ConfigProvider.get(config_names.THUNDRA_TEST_STATUS_REPORT_FREQUENCY)
        self.t = None


    def start(self, start_immediately=False):
        if not self.t:
            if start_immediately:
                self.t = threading.Timer(0, self.report_status)
            else:
                self.t = threading.Timer(self.delay, self.report_status)
            self.t.daemon = True
            self.t.start()


    def stop(self):
        if self.t:
            try:
                if self.t.is_alive():
                    self.t.cancel()
            except Exception as e:
                utils.print_debug_message_to_console("Error occured while canceling Status Reporter")
                pass
            finally:
                self.t = None


    def report_status(self):
        try:
            test_wrapper = TestWrapper.get_instance()
            status_time = utils.current_milli_time()
            test_run_status = TestRunStatus(
                id = TestRunnerSupport.test_run_scope.id,
                project_id = TestRunnerSupport.get_project_id_from_config(),
                task_id = TestRunnerSupport.test_run_scope.task_id,
                start_timestamp= TestRunnerSupport.test_run_scope.start_timestamp,
                status_timestamp= status_time,
                total_count= TestRunnerSupport.test_run_scope.context.total_count.value,
                successful_count= TestRunnerSupport.test_run_scope.context.successful_count.value,
                failed_count = TestRunnerSupport.test_run_scope.context.failed_count.value,
                ignored_count= TestRunnerSupport.test_run_scope.context.ignored_count.value,
                aborted_count= TestRunnerSupport.test_run_scope.context.aborted_count.value,
                host_name = TestRunnerSupport.HOST_NAME,
                environment_info= EnvironmentSupport.environment_info,
                # TODO tags
            )
            test_wrapper.send_test_run_data(test_run_status)
        except Exception as err:
            LOGGER.error("Couldn't send test run status: ".format(err))
        finally:
            self.stop()
            self.start()


class TestRunnerSupport:

    HOST_NAME = socket.gethostname()

    # TODO 
    '''
        For now, this design not support the parallell execution. 
        Test suite execution context and test case execution context may be 
        stored in pytest item object.
    '''
    test_suite_execution_context = None
    test_suite_application_info = None
    test_run_scope = None
    status_reporter = None
    
    @staticmethod
    def get_project_id_from_config():
        return ConfigProvider.get(config_names.THUNDRA_TEST_PROJECT_ID)

    @staticmethod
    def get_project_max_span_count():
        return ConfigProvider.get(config_names.THUNDRA_TEST_SPAN_COUNT_MAX)


    @classmethod
    def set_test_suite_execution_context(cls, execution_context):
        cls.test_suite_execution_context = execution_context


    @classmethod
    def set_test_suite_application_info(cls, application_info):
        cls.test_suite_application_info = application_info


    @classmethod
    def clear_test_run(cls):
        cls.test_run_scope = None


    @classmethod
    def clear_state(cls):
        cls.test_suite_execution_context = None
        cls.test_suite_application_info = None


    @staticmethod
    def do_get_test_run_id():
        test_run_id = None
        try:
            environment_info = EnvironmentSupport.environment_info
            if environment_info != None:
                test_run_id = environment_info.test_run_id
            if test_run_id == None:
                test_run_id = utils.create_uuid4()
        except Exception as err:
            LOGGER.error("Couldn't get test run id: {}".format(err))
            pass
        return test_run_id


    @classmethod
    def start_test_run(cls):
        try:
            test_wrapper = TestWrapper.get_instance()
            context = TestRunContext()
            id = cls.do_get_test_run_id()
            task_id = utils.create_uuid4()
            current_time = utils.current_milli_time()
            cls.test_run_scope = _TestRunScope(id, task_id, current_time, context)
            environment = EnvironmentSupport.environment_info if EnvironmentSupport.environment_info != None else None
            test_run_start = TestRunStart(
                cls.test_run_scope.id,
                cls.get_project_id_from_config(),
                cls.test_run_scope.task_id,
                cls.test_run_scope.start_timestamp,
                cls.HOST_NAME,
                environment
            )
            test_wrapper.send_test_run_data(test_run_start)
            if cls.status_reporter:
                cls.status_reporter.stop()
            else:
                cls.status_reporter = _StatusReporter()
            cls.status_reporter.start(start_immediately=True)
        except Exception as err:
            LOGGER.error("Couldn't start test run properly: {}".format(err))
            pass
    

    @classmethod
    def finish_current_test_run(cls):
        try:
            test_run_context = cls.get_test_run_context()
            if test_run_context:
                test_run_result = TestRunResult(
                    total_count = test_run_context.total_count.value,
                    successful_count = test_run_context.successful_count.value,
                    failed_count = test_run_context.failed_count.value,
                    ignored_count = test_run_context.ignored_count.value,
                    aborted_count = test_run_context.aborted_count.value
                ) 
                cls.finish_test_run(test_run_result)
        except Exception as err:
            LOGGER.error("Couldn't finish test run properly: {}".format(err))
            pass


    @classmethod
    def finish_test_run(cls, test_run_result):
        try:
            test_wrapper = TestWrapper.get_instance()
            finish_time = utils.current_milli_time()
            if cls.test_run_scope:
                if cls.status_reporter:
                    try:
                        cls.status_reporter.stop()
                    finally:
                        cls.status_reporter = None
                test_run_finish = TestRunFinish(
                    id = cls.test_run_scope.id,
                    project_id = cls.get_project_id_from_config(),
                    task_id = cls.test_run_scope.task_id,
                    start_timestamp= cls.test_run_scope.start_timestamp,
                    finish_timestamp= finish_time,
                    duration = finish_time - cls.test_run_scope.start_timestamp,
                    total_count= test_run_result.total_count,
                    successful_count= test_run_result.successful_count,
                    failed_count = test_run_result.failed_count,
                    ignored_count= test_run_result.ignored_count,
                    aborted_count= test_run_result.aborted_count,
                    host_name = cls.HOST_NAME,
                    environment_info= EnvironmentSupport.environment_info,
                    # TODO tags
                )
                test_wrapper.send_test_run_data(test_run_finish)
        except Exception as err:
            LOGGER.error("Thundra foresight finist test run error: {}".format(err))
            pass
        finally:
            cls.test_run_scope = None


    @classmethod
    def get_test_run_context(cls):
        if cls.test_run_scope:
            return cls.test_run_scope.context
        return None


    @classmethod 
    def get_test_run_id(cls):
        if cls.test_run_scope:
            return cls.test_run_scope.id
        return None


    @classmethod
    def get_test_run_task_id(cls):
        if cls.test_run_scope.task_id:
            return cls.test_run_scope.task_id
        return None