from thundra.application.application_info import ApplicationInfo
from thundra.application.application_info_provider import ApplicationInfoProvider
from thundra.opentracing.tracer import ThundraTracer
from thundra.foresight.test_runner_support import TestRunnerSupport

import uuid, os
import pytest


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
        return cls.TEST_APP_ID_PREFIX + cls.get_test_class_application_name(request)


    @classmethod
    def get_test_application_instance_id(cls, request):
        return cls.TEST_APP_INSTANCE_ID_PREFIX + cls.get_test_class_application_name(request)


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
    def get_test_application_resource_name(cls, request):
        return cls.get_test_method_name(request)


    @classmethod
    def get_test_name(cls, request):
        return cls.get_test_method_name(request)


    @classmethod
    def create_test_runner_application_info(cls, session):
        return cls.get_test_application_info(session)


    @classmethod
    def get_current_test_suite_context(cls):
        tracer = ThundraTracer.get_instance()
        test_suite_context = None
        current_span = tracer.get_active_span()
        if (current_span != None
                and cls.TEST_SUITE_DOMAIN_NAME == current_span.domain_name):
            test_suite_context = current_span.get(cls.TEST_SUITE_CONTEXT_PROP_NAME)
        return test_suite_context