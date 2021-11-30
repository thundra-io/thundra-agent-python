from foresight.constants.constants import ForesightConstants
from thundra.plugins.config.log_config import LogConfig
from thundra.wrappers.base_wrapper import BaseWrapper
import thundra.wrappers.wrapper_utils as wrapper_utils
from thundra.context.plugin_context import PluginContext
from thundra.application.global_application_info_provider import GlobalApplicationInfoProvider
from thundra.context.execution_context_manager import ExecutionContextManager
from thundra.context.tracing_execution_context_provider import TracingExecutionContextProvider
from foresight.context import (TestSuiteExecutionContext, TestCaseExecutionContext)
from foresight.sampler.max_count_aware_sampler import MaxCountAwareSampler 
from thundra.config.config_provider import ConfigProvider
from thundra.config import config_names
from foresight.constants.constants import ForesightConstants
import foresight.utils.generic_utils as utils
import logging

logger = logging.getLogger(__name__)

class TestWrapper(BaseWrapper):

    """
        Foresight wrapper util class. It keeps all the generic information for execution of test. 
        Creating test suite and test case, change application info, start and finish trace and invocation plugins.
    """

    __instance = None

    @staticmethod
    def get_instance(*args, **kwargs):
        return TestWrapper.__instance if TestWrapper.__instance else TestWrapper(*args, **kwargs) 


    def __init__(self, *, plugin_executor=None, api_key=None, disable_trace=False, disable_metric=True, disable_log=True, opts=None, **ignored):
        super(TestWrapper, self).__init__(api_key, disable_trace, disable_metric, disable_log, opts)
        ExecutionContextManager.set_provider(TracingExecutionContextProvider()) #TODO
        self.application_info_provider = GlobalApplicationInfoProvider()
        self._set_application_info("Foresight", "TestSuite", "TestSuite")
        self.plugin_context = PluginContext(application_info=self.application_info_provider.get_application_info(),
                                            request_count=0,
                                            executor=plugin_executor,
                                            api_key=self.api_key
        )
        max_test_log_count = ConfigProvider.get(config_names.THUNDRA_TEST_LOG_COUNT_MAX)
        self.config.log_config = LogConfig(sampler=MaxCountAwareSampler(max_test_log_count))
        self.plugins = wrapper_utils.initialize_plugins(self.plugin_context, disable_trace, disable_metric, disable_log,
                                                        config=self.config)
        TestWrapper.__instance = self


    def _set_application_info(self, application_class_name, application_domain_name, application_name):
        try:
            import pytest
            self.application_info_provider.update({
                "applicationClassName": application_class_name,
                "applicationDomainName": application_domain_name,
                "applicationName": application_name,
                "applicationVersion": pytest.__version__
            })
            self.application_info_provider.update({
                "applicationId": self._get_default_application_id()
            })
        except Exception as err:
            logger.error("Test wrapper utils application info set error: {}".format(err))
            pass


    def _get_default_application_id(self):
        try:
            application_info = self.application_info_provider.get_application_info()
            application_id = "python:test:pytest:{}:{}".format(application_info.get("applicationClassName"), application_info.get("applicationName"))
            return application_id.lower()
        except Exception as err:
            logger.error("get default application id error: {}".format(err))
            pass
        return "python:test:pytest:{}".format(utils.create_uuid4())


    def change_app_info(self, application_info):
        """It shall be used for when changing flow form test suite to test case or vice-versa.

        Args:
            application_info (ApplicationInfo): Thundra application info
        """
        try:
            self.application_info_provider.update(application_info.to_json())
        except Exception as err:
            logger.error("Test wrapper application info change error: {}".format(err))
            pass


    def create_test_suite_execution_context(self, test_suite_name=None):
        """ Creating test suite execution context

        Args:
            test_suite_name (str, optional): Unique test suite name. Defaults to None.

        Returns:
            TestSuiteExecutionContext: [description]
        """
        try:
            transaction_id = utils.create_uuid4()
            start_timestamp = utils.current_milli_time()
            return TestSuiteExecutionContext(
                transaction_id = transaction_id,
                start_timestamp = start_timestamp,
                node_id = test_suite_name
            )
        except Exception as err:
            logger.error("create test suite execution context error: {}".format(err))
            pass


    def create_test_case_execution_context(self, name, test_suite_name, test_case_id, app_info, parent_transaction_id=None):
        """Creating test case execution context

        Args:
            name (str): Test case name
            test_suite_name (str): unique test suite name
            test_case_id (str): unique test case id
            app_info (ApplicationInfo): Thundra application info
            parent_transaction_id (str, optional): Parent span transaction id for Thundra apm. Defaults to None.

        Returns:
            TestCaseExecutionContext: Store execution context for test case.
        """
        try:
            transaction_id = utils.create_uuid4()
            start_timestamp = utils.current_milli_time()
            test_class = app_info.application_class_name if app_info.application_class_name else None
            return TestCaseExecutionContext(
                transaction_id = transaction_id,
                start_timestamp = start_timestamp,
                test_suite_name = test_suite_name,
                node_id = test_case_id,
                parent_transaction_id = parent_transaction_id,
                name = name,
                method = ForesightConstants.TEST_OPERATION_NAME,
                test_class = test_class
            )
        except Exception as err:
            logger.error("create test case execution context error: {}".format(err))
            pass


    def start_trace(self, execution_context, tracer):
        """Calling after thundra trace pluging has been called by execute_hook. Create trace span.

        Args:
            execution_context (TestSuiteExecutionContext | TestSuiteExecutionContext): Execution context
            tracer (ThundraTracer): Thundra Tracer
        """
        try:
            operation_name = execution_context.get_operation_name()
            trace_id = utils.create_uuid4()
            scope = tracer.start_active_span(
                operation_name=operation_name,
                start_time=execution_context.start_timestamp,
                trace_id=trace_id,
                execution_context=execution_context,
                transaction_id=execution_context.transaction_id,
                finish_on_close=False,
            )
            root_span = scope.span
            app_info = self.application_info_provider.get_application_info()
            root_span.class_name = app_info.get("applicationClassName")
            root_span.domain_name = app_info.get("applicationDomainName")
            root_span.service_name = app_info.get("applicationName")
            execution_context.span_id = root_span.context.span_id
            execution_context.root_span = root_span
            execution_context.scope = scope
            execution_context.trace_id = trace_id
            
            root_span = execution_context.root_span
        except Exception as err:
            logger.error("Test wrapper start trace error: {}".format(err))
            pass


    def finish_trace(self, execution_context):
        """Finish trace.

        Args:
            execution_context (TestSuiteExecutionContext | TestSuiteExecutionContext): Execution context
        """
        try:
            root_span = execution_context.root_span
            scope = execution_context.scope
            try:
                root_span.finish(f_time=execution_context.finish_timestamp)
            except Exception:
                # TODO: handle root span finish errors
                pass
            finally:
                scope.close()
        except Exception as err:
            logger.error("test wrapper finish trace error: {}".format(err))
            pass


    def start_invocation(self, execution_context):
        """Calling after thundra invocation pluging has been called by execute_hook. Create trace span.

        Args:
            execution_context (TestSuiteExecutionContext | TestSuiteExecutionContext): Execution context
        """
        try:
            execution_context.invocation_data = wrapper_utils.create_invocation_data(self.plugin_context, execution_context)
        except Exception as err:
            logger.error("test wrapper start invocation error: {}".format(err))
            pass


    def finish_invocation(self, execution_context):
        """Finish invocation.

        Args:
            execution_context (TestSuiteExecutionContext | TestSuiteExecutionContext): Execution context
        """
        try:
            wrapper_utils.finish_invocation(execution_context)
        except Exception as err:
            logger.error("finish invocation error: {}".format(err))
            pass


    def before_test_process(self, execution_context):
        """Invoke trace and invocation plugings before each test suite and test case.

        Args:
            execution_context (TestSuiteExecutionContext | TestCaseExecutionContext): Thundra test execution context
        """
        try:
            self.execute_hook("before:invocation", execution_context)
        except Exception as err:
            logger.error("test wrapper before test process: {}".format(err))
            pass


    def after_test_process(self, execution_context):
        """Send collected data about test suit or test case after each finish.

        Args:
            execution_context (TestSuiteExecutionContext | TestCaseExecutionContext): Thundra test execution context
        """
        try:
            self.prepare_and_send_reports_async(execution_context)
        except Exception as err:
            logger.error("test wrapper after test process error: {}".format(err))
            pass


    def send_test_run_data(self, test_run_event):
        """Send test run data. test_run_monitoring data has been updated by application info because
         reporter has been used tih info whilst preparing composite data. 

        Args:
            test_run_event (TestRunStart, TestRunStatus, TestRunFinish): Tests event data
        """
        try:
            test_run_monitoring_data = test_run_event.get_monitoring_data()
            self.reporter.send_reports([test_run_monitoring_data], test_run_event = True)
        except Exception as err:
            logger.error("test wrapper send test run data error: {}".format(err))
            pass