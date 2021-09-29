from thundra.application.application_info import ApplicationInfo
from thundra.application.application_info_provider import ApplicationInfoProvider
from thundra.foresight.test_runner_support import TestRunnerSupport
from thundra.context.execution_context_manager import ExecutionContextManager
from thundra.foresight.test_runner_tags import TestRunnerTags
from thundra.foresight.utils.handler_utils import HandlerUtils
import thundra.foresight.pytest_integration.constants as constants
import thundra.foresight.utils.generic_utils as utils
import os, pytest


THUNDRA_SCOPE = "x-thundra-scope"


class SpanManager:
    
    @staticmethod
    def handle_fixture_and_inject_span(handler, app_info=None, span_tags=None, request=None):
        scope = handler(app_info, span_tags)
        setattr(request, THUNDRA_SCOPE, scope)

    @staticmethod
    def extract_scope(request):
        return getattr(request, THUNDRA_SCOPE, None)


class PytestHelper:

    TEST_APP_ID_PREFIX = "python:test:pytest:"
    TEST_APP_INSTANCE_ID_PREFIX = utils.create_uuid4() + ":"
    TEST_APP_STAGE = "test"
    TEST_APP_VERSION = pytest.__version__
    TEST_FIXTURE_DOMAIN_NAME = "TestFixture"
    TEST_DOMAIN_NAME = "Test"
    TEST_SUITE_DOMAIN_NAME = "TestSuite"
    TEST_CLASS_NAME = "Pytest"
    TEST_OPERATION_NAME = "RunTest"
    MAX_TEST_METHOD_NAME = 100
    TEST_SUITE_CONTEXT_PROP_NAME = "THUNDRA::TEST_SUITE_CONTEXT"
    TEST_OPERATION_NAME_INDEX = 2
    TEST_SUITE = "module"
    TEST_CASE = "function"
    PYTEST_STARTED = False


    @staticmethod
    def get_test_application_name(request):
        return request.nodeid.replace("::", os.sep)


    @classmethod
    def get_test_application_id(cls, request):
        return cls.TEST_APP_ID_PREFIX + cls.get_test_application_name(request)


    @classmethod
    def get_test_application_instance_id(cls, request):
        return cls.TEST_APP_INSTANCE_ID_PREFIX + cls.get_test_application_name(request)


    @classmethod
    def get_test_application_info(cls, request):
        domain_name = None
        application_id = None
        if request.scope == cls.TEST_SUITE:
            domain_name = cls.TEST_SUITE_DOMAIN_NAME
            application_id = cls.get_test_application_id(request)
        if request.scope == cls.TEST_CASE:
            domain_name = cls.TEST_DOMAIN_NAME
        return ApplicationInfo(
            application_id,
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


    @staticmethod
    def get_test_fixture_application_name(request):
        return request.fixturename


    @classmethod
    def get_test_fixture_application_instance_id(cls, request):
        return cls.TEST_APP_INSTANCE_ID_PREFIX + cls.get_test_fixture_application_name(request)


    @classmethod
    def get_test_fixture_application_info(cls, request):
        return ApplicationInfo(
            None,
            cls.get_test_fixture_application_instance_id(request),
            cls.TEST_FIXTURE_DOMAIN_NAME,
            cls.TEST_CLASS_NAME,
            cls.get_test_fixture_application_name(request),
            cls.TEST_APP_VERSION,
            cls.TEST_APP_STAGE,
            ApplicationInfoProvider.APPLICATION_RUNTIME,
            ApplicationInfoProvider.APPLICATION_RUNTIME_VERSION,
            None,
        )


    @classmethod
    def get_test_method_name(cls, request):
        nodeid = cls.get_test_application_name(request)
        if len(nodeid) > cls.MAX_TEST_METHOD_NAME:
            nodeid = "..." + nodeid[(len(nodeid)-cls.MAX_TEST_METHOD_NAME) + 3:]
        return nodeid


    @classmethod
    def get_test_name(cls, request):
        return cls.get_test_method_name(request)

    
    @staticmethod
    def session_setup(executor, api_key=None):
        HandlerUtils.test_setup(executor, api_key)


    @classmethod
    def session_teardown(cls):
        HandlerUtils.test_teardown()


    @classmethod
    def start_test_suite_span(cls, item):
        test_suite_id = item.nodeid
        app_info = cls.get_test_application_info(item)
        HandlerUtils.start_test_suite_span(test_suite_id, app_info)


    @classmethod
    def start_before_all_span(cls, request):
        app_info = cls.get_test_fixture_application_info(request).to_json()
        span_tags = {TestRunnerTags.TEST_SUITE: request.node.nodeid}
        SpanManager.handle_fixture_and_inject_span(HandlerUtils.start_before_all_span, app_info, span_tags,
            request)


    @staticmethod
    def finish_before_all_span(request):
        scope = SpanManager.extract_scope(request)
        HandlerUtils.finish_before_all_span(scope)


    @classmethod
    def start_after_all_span(cls, request):
        app_info = cls.get_test_fixture_application_info(request).to_json()
        span_tags = {TestRunnerTags.TEST_SUITE: request.node.nodeid}
        SpanManager.handle_fixture_and_inject_span(HandlerUtils.start_after_all_span, app_info, span_tags,
            request)


    @staticmethod
    def finish_after_all_span(request):
        scope = SpanManager.extract_scope(request)
        HandlerUtils.finish_after_all_span(scope)


    @staticmethod
    def finish_test_suite_span():
        HandlerUtils.finish_test_suite_span()


    @classmethod
    def start_test_span(cls, item):
        if not hasattr(item, constants.THUNDRA_TEST_STARTED):
            setattr(item, constants.THUNDRA_TEST_STARTED, True)
            name = item.location[2]
            test_suite_name = item.location[0]
            test_case_id = item.nodeid
            app_info = cls.get_test_application_info(item)
            HandlerUtils.start_test_span(name, test_suite_name, test_case_id, app_info)


    @classmethod
    def start_before_each_span(cls, request):
        app_info = cls.get_test_fixture_application_info(request).to_json()
        span_tags = { TestRunnerTags.TEST_SUITE: request.node.location[0] }
        SpanManager.handle_fixture_and_inject_span(HandlerUtils.start_before_each_span, app_info, span_tags,
            request)


    @staticmethod
    def finish_before_each_span(request):
        scope = SpanManager.extract_scope(request)
        HandlerUtils.finish_before_each_span(scope)


    @classmethod
    def start_after_each_span(cls, request):
        app_info = cls.get_test_fixture_application_info(request).to_json()
        span_tags = { TestRunnerTags.TEST_SUITE: request.node.location[0] }
        SpanManager.handle_fixture_and_inject_span(HandlerUtils.start_after_each_span, app_info, span_tags,
            request)  


    @classmethod
    def finish_after_each_span(cls, request):
        scope = SpanManager.extract_scope(request)
        span = scope.span
        span.set_tag(TestRunnerTags.TEST_NAME, cls.get_test_method_name(request.node))
        HandlerUtils.finish_after_each_span(scope)


    @staticmethod
    def finish_test_span(item):
        if not hasattr(item, constants.THUNDRA_TEST_ALREADY_FINISHED):
            setattr(item, constants.THUNDRA_TEST_ALREADY_FINISHED, True)
            HandlerUtils.finish_test_span()
