from thundra.application.application_info import ApplicationInfo
from thundra.application.application_info_provider import ApplicationInfoProvider
from thundra.opentracing.tracer import ThundraTracer
from thundra.foresight.test_runner_support import TestRunnerSupport
from thundra.foresight.environment.environment_info_support import EnvironmentSupport
from thundra.foresight.util.test_wrapper_utils import TestWrapperUtils
from thundra.context.execution_context_manager import ExecutionContextManager
from thundra.foresight.test_runner_tags import TestRunnerTags

import uuid, os
import pytest


class HandleSpan:

    @staticmethod
    def create_span(operation_name, execution_context):
        test_wrapper_utils = TestWrapperUtils.get_instance()
        app_info = test_wrapper_utils.application_info_provider.get_application_info()
        tracer = ThundraTracer().get_instance()
        parent_span = tracer.get_active_span()

        scope =  tracer.start_active_span(
            child_of= parent_span,
            operation_name=operation_name,
            start_time=execution_context.start_timestamp,
            trace_id=str(uuid.uuid4()),
            transaction_id=execution_context.transaction_id,
            execution_context=execution_context
        )
        scope.span.domain_name = app_info.get("applicationDomainName")
        scope.span.class_name = app_info.get("applicationClassName")
        return scope.span


    @staticmethod
    def finish_span(span, tagName):
        span.finish()
        context = ExecutionContextManager.get()
        if not context or not context.invocation_data:
            #TODO Add log
            return

        invocation_data = context.invocation_data
        if invocation_data:
            duration = span.get_duration()
            current_duration = 0
            if tagName in invocation_data["tags"]:
                current_duration = invocation_data["tags"][tagName]
            duration = duration + current_duration
            invocation_data["tags"][tagName] = duration


class PytestHelper:

    TEST_APP_ID_PREFIX = "python:test:pytest:"
    TEST_APP_INSTANCE_ID_PREFIX = str(uuid.uuid4()) + ":"
    TEST_APP_STAGE = "test"
    TEST_APP_VERSION = pytest.__version__
    TEST_DOMAIN_NAME = "Test"
    TEST_SUITE_DOMAIN_NAME = "TestSuite"
    TEST_CLASS_NAME = "Pytest"
    TEST_OPERATION_NAME = "RunTest"
    TEST_BEFORE_ALL_RULE_OPERATION_NAME = "beforeAllRule"
    TEST_BEFORE_ALL_OPERATION_NAME = "beforeAll"
    TEST_BEFORE_EACH_RULE_OPERATION_NAME = "beforeEachRule"
    TEST_BEFORE_EACH_OPERATION_NAME = "beforeEach"
    TEST_AFTER_EACH_OPERATION_NAME = "afterEach"
    TEST_AFTER_EACH_RULE_OPERATION_NAME = "afterEachRule"
    TEST_AFTER_ALL_OPERATION_NAME = "afterAll"
    TEST_AFTER_ALL_RULE_OPERATION_NAME = "afterAllRule"
    MAX_TEST_METHOD_NAME = 100
    TEST_SUITE_CONTEXT_PROP_NAME = "THUNDRA::TEST_SUITE_CONTEXT"
    TEST_OPERATION_NAME_INDEX = 2
    TEST_SUITE = "module"
    TEST_CASE = "function"


    @staticmethod
    def get_test_application_name(request):
        return request.node.nodeid.replace("::", os.sep)


    @classmethod
    def get_test_application_id(cls, request):
        return cls.TEST_APP_ID_PREFIX + cls.get_test_application_name(request)


    @classmethod
    def get_test_application_instance_id(cls, request):
        return cls.TEST_APP_INSTANCE_ID_PREFIX + cls.get_test_application_name(request)


    @classmethod
    def get_test_application_info(cls, request):
        domain_name = None
        if request.scope == cls.TEST_SUITE:
            domain_name = cls.TEST_SUITE_DOMAIN_NAME
        if request.scope == cls.TEST_CASE:
            domain_name = cls.TEST_DOMAIN_NAME
        return ApplicationInfo(
            cls.get_test_application_id(request),
            cls.get_test_application_instance_id(request),
            domain_name,
            cls.TEST_CLASS_NAME,
            cls.get_test_application_name(request),
            cls.TEST_APP_VERSION,
            cls.TEST_APP_STAGE,
            ApplicationInfoProvider.APPLICATION_RUNTIME,
            ApplicationInfoProvider.APPLICATION_RUNTIME_VERSION,
            None,
        )


    @classmethod
    def get_test_method_name(cls, request):
        nodeid = request.node.nodeid
        if request.scope == cls.TEST_CASE:
            nodeid = cls.get_test_application_name(nodeid)
        if len(nodeid) > cls.MAX_TEST_METHOD_NAME:
            nodeid = "..." + nodeid[(len(nodeid)-cls.MAX_TEST_METHOD_NAME) + 3:]
        return nodeid


    @classmethod
    def get_test_name(cls, request):
        return cls.get_test_method_name(request)

    
    @staticmethod
    def session_setup(executor, api_key=None):
        EnvironmentSupport.init()
        TestWrapperUtils(plugin_executor = executor)
        TestRunnerSupport.start_test_run()


    @staticmethod
    def session_teardown():
        TestRunnerSupport.finish_current_test_run()


    @classmethod
    def start_test_suite(cls, request):
        test_wrapper_utils = TestWrapperUtils.get_instance()
        test_suite_name = request.node.nodeid
        context = test_wrapper_utils.create_test_suite_execution_context(test_suite_name)
        test_wrapper_utils.before_test_process(context)
        app_info = cls.get_test_application_info(request)
        test_wrapper_utils.change_app_info(app_info)
        TestRunnerSupport.set_test_suite_application_info(app_info)
        TestRunnerSupport.set_test_suite_execution_context(context)
        ExecutionContextManager.set(context)


    @staticmethod
    def finish_test_suite():
        test_wrapper_utils = TestWrapperUtils.get_instance()
        app_info = TestRunnerSupport.test_suite_application_info
        context = TestRunnerSupport.test_suite_execution_context
        test_wrapper_utils.change_app_info(app_info)
        ExecutionContextManager.set(context)
        test_wrapper_utils.after_test_process(context)


    @classmethod
    def create_before_all_span(cls, request):
        context = ExecutionContextManager.get()
        span = HandleSpan.create_span(cls.TEST_BEFORE_ALL_OPERATION_NAME, context)
        span.set_tag(TestRunnerTags.TEST_SUITE, request.node.nodeid)

    
    @classmethod
    def create_after_all_span(cls, request):
        tracer = ThundraTracer.get_instance()
        span = tracer.get_active_span()
        HandleSpan.finish_span(span, TestRunnerTags.TEST_AFTER_ALL_DURATION)