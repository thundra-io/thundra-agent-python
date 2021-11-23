from foresight.environment.git.git_helper import GitHelper
from foresight.environment.environment_info import EnvironmentInfo
from foresight.utils.test_runner_utils import TestRunnerUtils
import os, logging
from foresight.utils.generic_utils import print_debug_message_to_console

LOGGER = logging.getLogger(__name__)

class CircleCIEnvironmentInfoProvider:
    ENVIRONMENT = "CircleCI"
    CIRCLE_REPOSITORY_URL_ENV_VAR_NAME = "CIRCLE_REPOSITORY_URL"
    CIRCLE_BRANCH_ENV_VAR_NAME = "CIRCLE_BRANCH"
    CIRCLE_SHA1_ENV_VAR_NAME = "CIRCLE_SHA1"
    CIRCLE_BUILD_URL_ENV_VAR_NAME = "CIRCLE_BUILD_URL"
    CIRCLE_BUILD_NUM_ENV_VAR_NAME = "CIRCLE_BUILD_NUM"

    @classmethod
    def get_test_run_id(cls, repo_url, commit_hash):
        configured_test_run_id = TestRunnerUtils.get_configured_test_run_id()
        if configured_test_run_id:
            return configured_test_run_id
        build_url = os.getenv(cls.CIRCLE_BUILD_URL_ENV_VAR_NAME)
        build_num = os.getenv(cls.CIRCLE_BUILD_NUM_ENV_VAR_NAME)
        test_run_key = TestRunnerUtils.string_concat_by_underscore(build_url, build_num)
        if test_run_key != "":
            return TestRunnerUtils.get_test_run_id(cls.ENVIRONMENT, repo_url, commit_hash,
                test_run_key)
        else:
            return TestRunnerUtils.get_default_test_run_id(cls.ENVIRONMENT, repo_url, commit_hash)
            

    @classmethod
    def build_env_info(cls):
        try:
            repo_url = os.getenv(cls.CIRCLE_REPOSITORY_URL_ENV_VAR_NAME)
            repo_name = GitHelper.extractRepoName(repo_url)
            branch = os.getenv(cls.CIRCLE_BRANCH_ENV_VAR_NAME)
            commit_hash = os.getenv(cls.CIRCLE_SHA1_ENV_VAR_NAME)
            commit_message = GitHelper.get_commit_message()

            if not branch:
                branch = GitHelper.get_branch()

            if not commit_hash:
                commit_hash = GitHelper.get_commit_hash()

            test_run_id = cls.get_test_run_id(repo_url, commit_hash)

            env_info = EnvironmentInfo(test_run_id, cls.ENVIRONMENT, repo_url, repo_name, branch, 
                commit_hash, commit_message)
            print_debug_message_to_console("CircleCI Environment info: {}".format(env_info.to_json()))
            return env_info
        except Exception as err:
            print_debug_message_to_console("CircleCI Unable to build environment info: {}".format(err))
            LOGGER.error("CircleCI Unable to build environment info: {}".format(err))
            pass
        return None