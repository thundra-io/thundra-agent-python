from thundra.foresight.environment.git.git_helper import GitHelper
from thundra.foresight.environment.environment_info import EnvironmentInfo
import logging
import os

LOGGER = logging.getLogger(__name__)

class GitlabEnvironmentInfoProvider:

    ENVIRONMENT = "GitLab"
    CI_REPOSITORY_URL_ENV_VAR_NAME = "CI_REPOSITORY_URL"
    CI_COMMIT_BRANCH_ENV_VAR_NAME = "CI_COMMIT_BRANCH"
    CI_COMMIT_REF_NAME_ENV_VAR_NAME = "CI_COMMIT_REF_NAME"
    CI_COMMIT_SHA_ENV_VAR_NAME = "CI_COMMIT_SHA"
    CI_COMMIT_MESSAGE_ENV_VAR_NAME = "CI_COMMIT_MESSAGE"
    CI_JOB_ID_ENV_VAR_NAME = "CI_JOB_ID"
    CI_JOB_URL_ENV_VAR_NAME = "CI_JOB_URL"

    environment_info = None

    @staticmethod
    def get_test_run_id(repo_url, commit_hash):
        pass #TODO

    @classmethod
    def _build_env_info(cls):
        try:
            repo_url = os.getenv(cls.CI_REPOSITORY_URL_ENV_VAR_NAME)
            repo_name = GitHelper.extractRepoName(repo_url)
            branch = os.getenv(cls.CI_COMMIT_BRANCH_ENV_VAR_NAME)
            if not branch:
                branch = os.getenv(cls.CI_COMMIT_REF_NAME_ENV_VAR_NAME)
            commit_hash = os.getenv(cls.CI_COMMIT_SHA_ENV_VAR_NAME)
            commit_message = os.getenv(cls.CI_COMMIT_MESSAGE_ENV_VAR_NAME)

            if not branch:
                branch = GitHelper.get_branch()
            
            if not commit_hash:
                commit_hash = GitHelper.get_commit_hash()

            if not commit_message:
                commit_message = GitHelper.get_commit_message()

            test_run_id = cls.get_test_run_id(repo_url, commit_hash)

            cls.environment_info = EnvironmentInfo(test_run_id, cls.ENVIRONMENT, repo_url, repo_name, branch, commit_hash, commit_message)
        except Exception as err:
            LOGGER.error("Unable to build environment info", err)
            cls.environment_info = None
            
GitlabEnvironmentInfoProvider._build_env_info()