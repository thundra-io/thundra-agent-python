from thundra.foresight.environment.git.git_helper import GitHelper
from thundra.foresight.environment.environment_info import EnvironmentInfo
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

    @staticmethod
    def get_test_run_id(repo_url, commit_hash):
        pass #TODO

    @classmethod
    def _build_env_info(cls):
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

CircleCIEnvironmentInfoProvider._build_env_info()