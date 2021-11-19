from thundra.application.application_info import ApplicationInfo
from thundra.application.application_info_provider import ApplicationInfoProvider
from foresight.test_runner_tags import TestRunnerTags
from foresight.utils.handler_utils import HandlerUtils
import foresight.pytest_integration.constants as pytest_constants
from foresight.constants.constants import ForesightConstants
import os, pytest, logging


logger = logging.getLogger(__name__)

class SpanManager:
    
    @staticmethod
    def handle_fixture_and_inject_span(handler, app_info=None, span_tags=None, request=None):
        """Handle beforeeach,aftereach, beforeall and afterall functions. Created span has been moved into request obj.

        Args:
            handler (Function): Beforeeach,aftereach, beforeall and afterall functions in utils.handler_utils
            app_info (ApplicationInfo, optional): Application Info. Defaults to None.
            span_tags (Dict, optional): [description]. Defaults to None.
            request (pytest.FixtureRequest, optional): Pytest FixtureRequest object that passed to wrapped fixture functions in pytest_integration.utils. Defaults to None.
        """
        try:
            scope = handler(app_info, span_tags)
            setattr(request, pytest_constants.THUNDRA_SCOPE, scope)
        except Exception as err:
            logger.error("Couldn't handle fixture and inject span for pytest: {}".format(err))
            pass


    @staticmethod
    def extract_scope(request):
        try:
            return getattr(request, pytest_constants.THUNDRA_SCOPE, None)
        except Exception as err:
            logger.error("Couldn't extract span from request for pytest: {}".format(err))
            pass
        return None


class PytestHelper:

    TEST_APP_ID_PREFIX = "python:test:pytest:"
    TEST_APP_VERSION = pytest.__version__
    TEST_CLASS_NAME = "Pytest"
    TEST_SUITE_PATH = 0
    TEST_OPERATION_NAME_INDEX = 2
    TEST_SUITE = "module"
    TEST_CASE = "function"
    PYTEST_STARTED = False
    PYTEST_COLLECT_ONLY = False


    @staticmethod
    def get_test_application_name(request):
        try:
            return request.nodeid.replace("::", os.sep)
        except Exception as err:
            logger.error("Couldn't get test application name for pytest: {}".format(err))
            pass
        return None

    @classmethod
    def get_test_application_id(cls, request):
        return cls.TEST_APP_ID_PREFIX + cls.get_test_application_name(request)


    @classmethod
    def get_test_application_instance_id(cls, request):
        return ForesightConstants.TEST_APP_INSTANCE_ID_PREFIX + cls.get_test_application_name(request)


    @classmethod
    def get_test_application_info(cls, request):
        try:
            domain_name = None
            application_id = None
            if request.scope == cls.TEST_SUITE:
                domain_name = ForesightConstants.TEST_SUITE_DOMAIN_NAME
                application_id = cls.get_test_application_id(request)
            elif request.scope == cls.TEST_CASE:
                domain_name = ForesightConstants.TEST_DOMAIN_NAME
            return ApplicationInfo(
                application_id,
                cls.get_test_application_instance_id(request),
                domain_name,
                cls.TEST_CLASS_NAME,
                cls.get_test_application_name(request),
                cls.TEST_APP_VERSION,
                ForesightConstants.TEST_APP_STAGE,
                ApplicationInfoProvider.APPLICATION_RUNTIME,
                ApplicationInfoProvider.APPLICATION_RUNTIME_VERSION,
                None,
            )
        except Exception as err:
            logger.error("Couldn't get application info for pytest: {}".format(err))
            pass

    @staticmethod
    def get_test_fixture_application_name(request):
        try:
            return request.fixturename
        except Exception as err:
            logger.error("Couldn't get fixture application name for pytest: {}".format(err))
            pass

    @classmethod
    def get_test_fixture_application_instance_id(cls, request):
        return ForesightConstants.TEST_APP_INSTANCE_ID_PREFIX + cls.get_test_fixture_application_name(request)


    @classmethod
    def get_test_fixture_application_info(cls, request):
        return ApplicationInfo(
            None,
            cls.get_test_fixture_application_instance_id(request),
            ForesightConstants.TEST_FIXTURE_DOMAIN_NAME,
            cls.TEST_CLASS_NAME,
            cls.get_test_fixture_application_name(request),
            cls.TEST_APP_VERSION,
            ForesightConstants.TEST_APP_STAGE,
            ApplicationInfoProvider.APPLICATION_RUNTIME,
            ApplicationInfoProvider.APPLICATION_RUNTIME_VERSION,
            None,
        )


    @classmethod
    def get_test_method_name(cls, request):
        try:
            nodeid = cls.get_test_application_name(request)
            if len(nodeid) > ForesightConstants.MAX_TEST_METHOD_NAME:
                nodeid = "..." + nodeid[(len(nodeid)-ForesightConstants.MAX_TEST_METHOD_NAME) + 3:]
            return nodeid
        except Exception as err:
            logger.error("Couldn't get method name for pytest: {}".format(err))
            pass
        return None 


    @classmethod
    def get_test_name(cls, request):
        return cls.get_test_method_name(request)


    @classmethod
    def check_pytest_started(cls):
        return cls.PYTEST_STARTED


    @classmethod
    def set_pytest_started(cls):
        cls.PYTEST_STARTED = True

    @classmethod
    def check_pytest_collect_only(cls):
        return cls.PYTEST_COLLECT_ONLY


    @classmethod
    def set_pytest_collect_only(cls):
        cls.PYTEST_COLLECT_ONLY = True

    @staticmethod
    def clear_test_case_state_for_thundra(item):
        delattr(item, pytest_constants.THUNDRA_TEST_RESULTED)
        delattr(item, pytest_constants.THUNDRA_TEST_STARTED)
        delattr(item, pytest_constants.THUNDRA_TEST_ALREADY_FINISHED)
        setattr(item, pytest_constants.THUNDRA_TEST_FINISH_IN_HELPER, True)
    

    @staticmethod
    def session_setup(executor, api_key=None):
        try:
            HandlerUtils.test_setup(executor, api_key)
        except Exception as err:
            logger.error("Couldn't setup the session for pytest: {}".format(err))
            pass


    @classmethod
    def session_teardown(cls):
        try:
            HandlerUtils.test_teardown()
        except Exception as err:
            logger.error("Error session teardown for pytest: {}".format(err))
            pass


    @classmethod
    def start_test_suite_span(cls, item):
        try:
            test_suite_id = item.nodeid
            app_info = cls.get_test_application_info(item)
            HandlerUtils.start_test_suite_span(test_suite_id, app_info)
        except Exception as err:
            logger.error("Couldn't start test suite span for pytest: {}".format(err))
            pass


    @classmethod
    def start_before_all_span(cls, request):
        try:
            app_info = cls.get_test_fixture_application_info(request).to_json()
            span_tags = {TestRunnerTags.TEST_SUITE: request.node.nodeid, TestRunnerTags.TEST_FIXTURE: request.fixturename}
            SpanManager.handle_fixture_and_inject_span(HandlerUtils.start_before_all_span, app_info, span_tags,
                request)
        except Exception as err:
            logger.error("Couldn't start before all span for pytest: {}".format(err))
            pass


    @staticmethod
    def finish_before_all_span(request):
        try:
            scope = SpanManager.extract_scope(request)
            HandlerUtils.finish_before_all_span(scope)
        except Exception as err:
            logger.error("Couldn't finish before all span for pytest: {}".format(err))
            pass


    @classmethod
    def start_after_all_span(cls, request):
        try:
            app_info = cls.get_test_fixture_application_info(request).to_json()
            span_tags = {TestRunnerTags.TEST_SUITE: request.node.nodeid, TestRunnerTags.TEST_FIXTURE: request.fixturename}
            SpanManager.handle_fixture_and_inject_span(HandlerUtils.start_after_all_span, app_info, span_tags,
                request)
        except Exception as err:
            logger.error("Couldn't start after all span for pytest: {}".format(err), err)
            pass


    @staticmethod
    def finish_after_all_span(request):
        try:
            scope = SpanManager.extract_scope(request)
            HandlerUtils.finish_after_all_span(scope)
        except Exception as err:
            logger.error("Couldn't finish after all span for pytest: {}".format(err))
            pass


    @staticmethod
    def finish_test_suite_span():
        try:
            HandlerUtils.finish_test_suite_span()
        except Exception as err:
            logger.error("Couldn't finish test suite span for pytest: {}".format(err))
            pass


    @classmethod
    def start_test_span(cls, item):
        try:
            if not hasattr(item, pytest_constants.THUNDRA_TEST_STARTED):
                setattr(item, pytest_constants.THUNDRA_TEST_STARTED, True)
                name = item.location[cls.TEST_OPERATION_NAME_INDEX]
                test_suite_name = item.location[cls.TEST_SUITE_PATH]
                test_case_id = item.nodeid
                app_info = cls.get_test_application_info(item)
                HandlerUtils.start_test_span(name, test_suite_name, test_case_id, app_info)
        except Exception as err:
            logger.error("Couldn't start test span for pytest: {}".format(err))
            pass


    @classmethod
    def start_before_each_span(cls, request):
        try:
            app_info = cls.get_test_fixture_application_info(request).to_json()
            span_tags = { TestRunnerTags.TEST_SUITE: request.node.location[cls.TEST_SUITE_PATH], TestRunnerTags.TEST_FIXTURE: request.fixturename}
            SpanManager.handle_fixture_and_inject_span(HandlerUtils.start_before_each_span, app_info, span_tags,
                request)
        except Exception as err:
            logger.error("Couldn't start before each span for pytest: {}".format(err))
            pass


    @staticmethod
    def finish_before_each_span(request):
        try:
            scope = SpanManager.extract_scope(request)
            HandlerUtils.finish_before_each_span(scope)
        except Exception as err:
            logger.error("Couldn't finish before each span for pytest: {}".format(err))
            pass


    @classmethod
    def start_after_each_span(cls, request):
        try:
            app_info = cls.get_test_fixture_application_info(request).to_json()
            span_tags = { TestRunnerTags.TEST_SUITE: request.node.location[cls.TEST_SUITE_PATH], TestRunnerTags.TEST_FIXTURE: request.fixturename}
            SpanManager.handle_fixture_and_inject_span(HandlerUtils.start_after_each_span, app_info, span_tags,
                request)  
        except Exception as err:
            logger.error("Couldn't start after each span for pytest: {}".format(err))
            pass


    @classmethod
    def finish_after_each_span(cls, request):
        try:
            scope = SpanManager.extract_scope(request)
            span = scope.span
            span.set_tag(TestRunnerTags.TEST_NAME, cls.get_test_method_name(request.node))
            HandlerUtils.finish_after_each_span(scope)
        except Exception as err:
            logger.error("Couldn't finish after each span for pytest: {}".format(err))
            pass


    @classmethod
    def finish_test_span(cls, item):
        try:
            if not hasattr(item, pytest_constants.THUNDRA_TEST_ALREADY_FINISHED):
                setattr(item, pytest_constants.THUNDRA_TEST_ALREADY_FINISHED, True)
                HandlerUtils.finish_test_span()
                cls.clear_test_case_state_for_thundra(item)
        except Exception as err:
            logger.error("Couldn't finish test span for pytest: {}".format(err))
            pass
