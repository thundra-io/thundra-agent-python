from uuid import uuid4
from foresight.environment.git.git_helper import GitHelper
from foresight.environment.environment_info import EnvironmentInfo
from foresight.utils.test_runner_utils import TestRunnerUtils
import os, logging
from foresight.utils.generic_utils import print_debug_message_to_console

LOGGER = logging.getLogger(__name__)

class AzureEnvironmentInfoProvider:

    ENVIRONMENT = "Azure"
    BUILD_BUILDID_ENV_VAR_NAME = "BUILD_BUILDID"
    BUILD_REPOSITORY_NAME_ENV_VAR_NAME = "BUILD_REPOSITORY_NAME"
    BUILD_REPOSITORY_URI_ENV_VAR_NAME = "BUILD_REPOSITORY_URI"
    BUILD_SOURCEBRANCHNAME_ENV_VAR_NAME = "BUILD_SOURCEBRANCHNAME"
    BUILD_SOURCEVERSION_ENV_VAR_NAME = "BUILD_SOURCEVERSION"
    BUILD_SOURCEVERSIONMESSAGE_ENV_VAR_NAME = "BUILD_SOURCEVERSIONMESSAGE"
    INVOCATION_ID_ENV_VAR_NAME = "INVOCATION_ID"
    BUILD_REPOSITORY_PROVIDER_ENV_VAR_NAME = "BUILD_REPOSITORY_PROVIDER"

    @classmethod
    def get_test_run_id(cls, repo_url, commit_hash, environment):
        configured_test_run_id = TestRunnerUtils.get_configured_test_run_id()
        if configured_test_run_id:
            return configured_test_run_id
        build_number = os.getenv(cls.BUILD_BUILDID_ENV_VAR_NAME)
        invocation_id = os.getenv(cls.INVOCATION_ID_ENV_VAR_NAME)
        test_run_key = cls.generate_test_run_key(invocation_id, build_number)
        if test_run_key:
            return TestRunnerUtils.get_test_run_id(environment, repo_url, commit_hash, test_run_key)
        else:
            return TestRunnerUtils.get_default_test_run_id(environment, repo_url, commit_hash)


    @staticmethod
    def generate_test_run_key(invocation_id=None, build_number=None):
        if invocation_id and build_number:
            return invocation_id + "-" + build_number
        elif invocation_id:
            return invocation_id
        elif build_number:
            return build_number
        else:
            return None

    @classmethod
    def build_env_info(cls):
        try:
            repo_url = os.getenv(cls.BUILD_REPOSITORY_URI_ENV_VAR_NAME)
            repo_name = os.getenv(cls.BUILD_REPOSITORY_NAME_ENV_VAR_NAME) or GitHelper.extractRepoName(repo_url)
            branch = os.getenv(cls.BUILD_SOURCEBRANCHNAME_ENV_VAR_NAME)
            commit_hash = os.getenv(cls.BUILD_SOURCEVERSION_ENV_VAR_NAME)
            commit_message = os.getenv(cls.BUILD_SOURCEVERSIONMESSAGE_ENV_VAR_NAME) or GitHelper.get_commit_message()
            repo_provider = os.getenv(cls.BUILD_REPOSITORY_PROVIDER_ENV_VAR_NAME)
            
            environment = cls.ENVIRONMENT + " - " + str(repo_provider) if repo_provider else cls.ENVIRONMENT

            if not branch:
                branch = GitHelper.get_branch()

            if not commit_hash:
                commit_hash = GitHelper.get_commit_hash()

            test_run_id = cls.get_test_run_id(repo_url, commit_hash, environment)

            env_info = EnvironmentInfo(test_run_id, environment, repo_url, repo_name, 
                branch, commit_hash, commit_message)
            print_debug_message_to_console("Azure Environment info: {}".format(env_info.to_json()))
            return env_info
        except Exception as err:
            print_debug_message_to_console("Unable to build environment info: {}".format(err))
            LOGGER.error("Unable to build environment info: {}".format(err))
            pass
        return None