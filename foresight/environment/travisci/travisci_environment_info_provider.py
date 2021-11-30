from foresight.environment.git.git_helper import GitHelper
from foresight.environment.environment_info import EnvironmentInfo
from foresight.utils.test_runner_utils import TestRunnerUtils 
import os, logging
from foresight.utils.generic_utils import print_debug_message_to_console


LOGGER = logging.getLogger(__name__)


class TravisCIEnvironmentInfoProvider:
    ENVIRONMENT = "TravisCI"
    TRAVIS_REPO_SLUG_VAR_NAME = "TRAVIS_REPO_SLUG"
    TRAVIS_PULL_REQUEST_BRANCH_ENV_VAR_NAME = "TRAVIS_PULL_REQUEST_BRANCH"
    TRAVIS_BRANCH_ENV_VAR_NAME = "TRAVIS_BRANCH"
    TRAVIS_COMMIT_ENV_VAR_NAME = "TRAVIS_COMMIT"
    TRAVIS_COMMIT_MESSAGE_ENV_VAR_NAME = "TRAVIS_COMMIT_MESSAGE"
    TRAVIS_BUILD_WEB_URL_ENV_VAR_NAME = "TRAVIS_BUILD_WEB_URL"
    TRAVIS_BUILD_ID_ENV_VAR_NAME = "TRAVIS_BUILD_ID"


    @classmethod
    def get_test_run_id(cls, repo_url, commit_hash):
        configured_test_run_id = TestRunnerUtils.get_configured_test_run_id()
        if configured_test_run_id:
            return configured_test_run_id
        build_web_url = os.getenv(cls.TRAVIS_BUILD_WEB_URL_ENV_VAR_NAME)
        build_id = os.getenv(cls.TRAVIS_BUILD_ID_ENV_VAR_NAME)
        test_run_key = TestRunnerUtils.string_concat_by_underscore(build_web_url, build_id)
        if test_run_key != "":
            return TestRunnerUtils.get_test_run_id(cls.ENVIRONMENT, repo_url, commit_hash, 
                test_run_key)
        else:
            return TestRunnerUtils.get_default_test_run_id(cls.ENVIRONMENT, repo_url, commit_hash)


    @classmethod
    def build_env_info(cls):
        try:
            repo_url = "https://github.com/{}.git".format(os.getenv(cls.TRAVIS_REPO_SLUG_VAR_NAME))
            repo_name = GitHelper.extractRepoName(repo_url)
            branch = os.getenv(cls.TRAVIS_PULL_REQUEST_BRANCH_ENV_VAR_NAME)
            commit_hash = os.getenv(cls.TRAVIS_COMMIT_ENV_VAR_NAME)
            commit_message = os.getenv(cls.TRAVIS_COMMIT_MESSAGE_ENV_VAR_NAME)

            if not branch:
                branch = GitHelper.get_branch()
            
            if not commit_hash:
                commit_hash = GitHelper.get_commit_hash()

            if not commit_message:
                commit_message = GitHelper.get_commit_message()

            test_run_id = cls.get_test_run_id(repo_url, commit_hash)
            
            env_info = EnvironmentInfo(test_run_id, cls.ENVIRONMENT, repo_url, 
                repo_name, branch, commit_hash, commit_message)
            print_debug_message_to_console("TravisCI Environment info: {}".format(env_info.to_json()))
            return env_info
        except Exception as err:
            print_debug_message_to_console("TravisCI Unable to build environment info: {}".format(err))
            LOGGER.error("TravisCI Unable to build environment info: {}".format(err))
            pass
        return None