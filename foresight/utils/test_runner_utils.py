from thundra.config.config_provider import ConfigProvider
from thundra.config import config_names
import foresight.utils.generic_utils as utils
import uuid, logging

LOGGER = logging.getLogger(__name__) 

class NULL_NAMESPACE:
    bytes = b''

class TestRunnerUtils:
    
    @staticmethod
    def get_configured_test_run_id():
        return ConfigProvider.get(config_names.THUNDRA_TEST_RUN_ID)

    
    @classmethod
    def get_test_run_id(cls, environment, repo_url, commit_hash, test_run_key):
        try:
            test_run_id_seed = cls.string_concat_by_underscore(environment, repo_url, 
                commit_hash, test_run_key)
            # UUID.nameUUIDFromBytes is used in java and its uuid version is 3. To keep compatibality, using uuid3.
            # https://stackoverflow.com/questions/27939281/reproduce-uuid-from-java-code-in-python
            return str(uuid.uuid3(NULL_NAMESPACE, test_run_id_seed))
        except Exception as err:
            LOGGER.error("Test run id could not be created by uuid: {}".format(err))
            pass
        return str(uuid.uuid4())


    @staticmethod
    def get_default_test_run_id(environment=None, repo_url=None, commit_hash=None):
        try:
            #TODO Find a way to generate uuid with parameters
            return utils.create_uuid4()
        except Exception as err:
            LOGGER.error("get_default_test_run_id couldn't created")
            pass


    @staticmethod
    def string_concat_by_underscore(*str_list):
        try:
            return "_".join(str_list)
        except Exception as err:
            LOGGER.error("test runner utils string concat error: {}".format(err))
            pass
        return ""