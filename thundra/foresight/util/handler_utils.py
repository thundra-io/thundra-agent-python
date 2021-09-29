from thundra.opentracing.tracer import ThundraTracer
from thundra.foresight.test_runner_support import TestRunnerSupport
from thundra.foresight.environment.environment_info_support import EnvironmentSupport
from thundra.foresight.util.test_wrapper_utils import TestWrapperUtils
from thundra.context.execution_context_manager import ExecutionContextManager
from thundra.foresight.test_runner_tags import TestRunnerTags
import thundra.foresight.utils as utils
import uuid


class HandlerUtils:

    TEST_BEFORE_ALL_OPERATION_NAME = "beforeAll"
    TEST_AFTER_ALL_OPERATION_NAME = "afterAll"
    TEST_BEFORE_EACH_OPERATION_NAME = "beforeEach"
    TEST_AFTER_EACH_OPERATION_NAME = "afterEach"


    @staticmethod
    def create_span(operation_name, app_info={}, span_tags=None):
        tracer = ThundraTracer().get_instance()
        execution_context = ExecutionContextManager.get()
        parent_transaction_id = execution_context.transaction_id if execution_context.transaction_id else None
        trace_id = execution_context.trace_id if execution_context.trace_id else str(uuid.uuid4())
        transaction_id = parent_transaction_id or str(uuid.uuid4())
        scope =  tracer.start_active_span(
            span_id=str(uuid.uuid4()),
            operation_name=operation_name,
            trace_id=trace_id,
            transaction_id=transaction_id,
            start_time=utils.current_milli_time(),
            execution_context = execution_context
        )
        span = scope.span
        span.domain_name = app_info.get("applicationDomainName")
        span.class_name = app_info.get("applicationClassName")
        span.service_name = app_info.get("applicationName")
        if span_tags:
            for key in span_tags.keys():
                span.set_tag(key, span_tags[key])
        return scope


    @staticmethod
    def finish_span(scope, tagName):
        context = ExecutionContextManager.get()
        current_span = scope.span
        current_span.finish(f_time=utils.current_milli_time())
        scope.close()
        if not context or not context.invocation_data:
            #TODO Add log
            return
        invocation_data = context.invocation_data
        if invocation_data:
            duration = current_span.get_duration()
            current_duration = 0
            if tagName in invocation_data["tags"]:
                current_duration = invocation_data["tags"][tagName]
            duration = duration + current_duration
            invocation_data["tags"][tagName] = duration


    @staticmethod
    def test_setup(executor, api_key=None):
        EnvironmentSupport.init()
        TestWrapperUtils(api_key=api_key, plugin_executor = executor)
        TestRunnerSupport.start_test_run()


    @classmethod
    def test_teardown(cls):
        if (TestRunnerSupport.test_suite_execution_context and 
            not TestRunnerSupport.test_suite_execution_context.completed):
            HandlerUtils.finish_test_suite_span()
        TestRunnerSupport.finish_current_test_run()


    @classmethod
    def start_test_suite_span(cls, test_suite_id, app_info):
        if not TestRunnerSupport.test_suite_execution_context:
            test_wrapper_utils = TestWrapperUtils.get_instance()
            context = test_wrapper_utils.create_test_suite_execution_context(test_suite_id)
            ExecutionContextManager.set(context)
            test_wrapper_utils.change_app_info(app_info)
            TestRunnerSupport.set_test_suite_application_info(app_info)
            TestRunnerSupport.set_test_suite_execution_context(context)
            test_wrapper_utils.before_test_process(context)


    @classmethod
    def start_before_all_span(cls, app_info, span_tags= None):
        cls.create_span(cls.TEST_BEFORE_ALL_OPERATION_NAME, app_info, span_tags)


    @classmethod
    def finish_before_all_span(cls, scope):
        cls.finish_span(scope, TestRunnerTags.TEST_BEFORE_ALL_DURATION)


    @classmethod
    def start_after_all_span(cls, test_suite_id, app_info, span_tags):
        context = TestRunnerSupport.get_test_suite_info(test_suite_id)
        ExecutionContextManager.set(context)
        cls.create_span(cls.TEST_AFTER_ALL_OPERATION_NAME, app_info, span_tags)


    @classmethod
    def finish_after_all_span(cls, scope):
        cls.finish_span(scope, TestRunnerTags.TEST_AFTER_ALL_DURATION)


    @staticmethod
    def finish_test_suite_span():
        test_wrapper_utils = TestWrapperUtils.get_instance()
        context = ExecutionContextManager.get()
        context.completed = True
        test_wrapper_utils.after_test_process(context)
        TestRunnerSupport.clear_state()


    @classmethod
    def start_test_span(cls, name, test_suite_name, test_case_id, app_info):
        test_wrapper_utils = TestWrapperUtils.get_instance()
        test_wrapper_utils.change_app_info(app_info)
        current_context = ExecutionContextManager.get()
        parent_transaction_id = current_context.invocation_data.get("transactionId")
        context = test_wrapper_utils.create_test_case_execution_context(name, test_suite_name, test_case_id, app_info, parent_transaction_id)   
        ExecutionContextManager.set(context)
        test_wrapper_utils.before_test_process(context)


    @classmethod
    def start_before_each_span(cls, app_info, span_tags=None):
        cls.create_span(cls.TEST_BEFORE_EACH_OPERATION_NAME, app_info, span_tags)


    @classmethod
    def finish_before_each_span(cls, scope):
        cls.finish_span(scope, TestRunnerTags.TEST_BEFORE_EACH_DURATION)


    @classmethod
    def start_after_each_span(cls, app_info, span_tags=None):
        cls.create_span(cls.TEST_AFTER_EACH_OPERATION_NAME, app_info, span_tags)


    @classmethod
    def finish_after_each_span(cls, scope):
        cls.finish_span(scope, TestRunnerTags.TEST_AFTER_EACH_DURATION)


    @staticmethod
    def finish_test_span():
        test_wrapper_utils = TestWrapperUtils.get_instance()
        context = ExecutionContextManager.get()
        test_wrapper_utils.after_test_process(context)
        app_info = TestRunnerSupport.test_suite_application_info
        context = TestRunnerSupport.test_suite_execution_context
        test_wrapper_utils.change_app_info(app_info)
        ExecutionContextManager.set(context)
