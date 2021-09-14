from thundra.wrappers.base_wrapper import BaseWrapper
import thundra.wrappers.wrapper_utils as wrapper_utils
from thundra.context.plugin_context import PluginContext
from thundra.application.global_application_info_provider import GlobalApplicationInfoProvider
from thundra.foresight import foresight_executor 
from thundra.context.execution_context_manager import ExecutionContextManager
from thundra.context.tracing_execution_context_provider import TracingExecutionContextProvider
from thundra.foresight.context import (TestSuiteExecutionContext, TestCaseExecutionContext)
import thundra.foresight.utils as utils
from uuid import uuid4

class TestWrapperUtils(BaseWrapper):

    __instance = None

    @staticmethod
    def get_instance(*args, **kwargs):
        print(TestWrapperUtils.__instance)
        if not TestWrapperUtils.__instance:
            TestWrapperUtils.__instance = TestWrapperUtils(*args, **kwargs)
        return TestWrapperUtils.__instance

    def __init__(self, *, api_key=None, disable_trace=False, disable_metric=True, disable_log=True, opts=None, **ignored):
        super(TestWrapperUtils, self).__init__(api_key, disable_trace, disable_metric, disable_log, opts)
        ExecutionContextManager.set_provider(TracingExecutionContextProvider) #TODO
        self.application_info_provider = GlobalApplicationInfoProvider()
        self._set_application_info("Foresight", "TestSuite", "TestSuite")
        self.plugin_context = PluginContext(application_info=self.application_info_provider.get_application_info(),
                                            request_count=0,
                                            executor=foresight_executor,
                                            api_key=self.api_key
        )
        self.plugins = wrapper_utils.initialize_plugins(self.plugin_context, disable_trace, disable_metric, disable_log,
                                                        config=self.config)


    def _set_application_info(self, application_class_name, application_domain_name, application_name):
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


    def _get_default_application_id(self):
        application_info = self.application_info_provider.get_application_info()
        application_id = "python:test:pytest:{}:{}".format(application_info.get("applicationClassName"), application_info.get("applicationName"))
        return application_id.lower()


    def change_app_info(self, application_info):
        self.application_info_provider.update(application_info.to_json())
        

    def create_test_suite_execution_context(self, test_suite_name):
        transaction_id = str(uuid4())
        start_timestamp = utils.current_milli_time()
        return TestSuiteExecutionContext(
            transaction_id = transaction_id,
            start_timestamp = start_timestamp,
            test_suite_name = test_suite_name
        )


    def create_test_case_execution_context(self, test_suite_name, test_case_id):
        transaction_id = str(uuid4)
        start_timestamp = utils.current_milli_time()
        return TestCaseExecutionContext(
            transaction_id = transaction_id,
            start_timestamp = start_timestamp,
            test_suite_name = test_suite_name,
            id = test_case_id
        )


    def before_test_process(self, execution_context):
        self.plugin_context.request_count += 1
        self.execute_hook("before:invocation", execution_context)


    def after_test_process(self, execution_context):
        self.prepare_and_send_reports(execution_context)
        execution_context.reports = []


    def send_test_run_data(self, test_run_event):
        test_run_monitoring_data = test_run_event.get_monitoring_data()
        self.reporter.send_reports([test_run_monitoring_data])