from thundra.foresight.environment.git.git_helper import GitHelper
from thundra.foresight.environment.environment_info import EnvironmentInfo
from thundra.foresight.util.test_runner_utils import TestRunnerUtils
import os, logging

LOGGER = logging.getLogger(__name__)

class CircleCIEnvironmentInfoProvider:
    ENVIRONMENT = "CircleCI"
    CIRCLE_REPOSITORY_URL_ENV_VAR_NAME = "CIRCLE_REPOSITORY_URL"
    CIRCLE_BRANCH_ENV_VAR_NAME = "CIRCLE_BRANCH"
    CIRCLE_SHA1_ENV_VAR_NAME = "CIRCLE_SHA1"
    CIRCLE_BUILD_URL_ENV_VAR_NAME = "CIRCLE_BUILD_URL"
    CIRCLE_BUILD_NUM_ENV_VAR_NAME = "CIRCLE_BUILD_NUM"
    environment_info = None

    @classmethod
    def get_test_run_id(cls, repo_url, commit_hash):
        configured_test_run_id = TestRunnerUtils.get_configured_test_run_id()
        if configured_test_run_id:
            return configured_test_run_id
        build_url = os.getenv(cls.CIRCLE_BUILD_URL_ENV_VAR_NAME)
        build_num = os.getenv(cls.CIRCLE_BUILD_NUM_ENV_VAR_NAME)
        if build_url or build_url:
            return TestRunnerUtils.get_test_run_id(cls.ENVIRONMENT, repo_url, commit_hash,
                TestRunnerUtils.string_concat_by_underscore(build_url, build_num))
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

            cls.environment_info = EnvironmentInfo(test_run_id, cls.ENVIRONMENT, repo_url, repo_name, branch, 
                commit_hash, commit_message)
        except Exception as err:
            LOGGER.error("Unable to build environment info", err)
            cls.environment_info = None