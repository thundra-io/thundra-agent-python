import foresight.utils.generic_utils as utils

class ForesightConstants:
    TEST_APP_INSTANCE_ID_PREFIX = utils.create_uuid4() + ":"
    TEST_APP_STAGE = "test"
    TEST_FIXTURE_DOMAIN_NAME = "TestFixture"
    TEST_DOMAIN_NAME = "Test"
    TEST_SUITE_DOMAIN_NAME = "TestSuite"
    TEST_OPERATION_NAME = "RunTest"    
    MAX_TEST_METHOD_NAME = 100
