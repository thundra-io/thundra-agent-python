from thundra.foresight.environment.environment_info import EnvironmentInfo
from thundra.foresight.environment.git.git_helper import GitHelper
import os
import logging

LOGGER = logging.getLogger(__name__)

class JenkinsEnvironmentInfoProvider:
    
    ENVIRONMENT = "Jenkins"
    GIT_URL_ENV_VAR_NAME = "GIT_URL"
    GIT_URL_1_ENV_VAR_NAME = "GIT_URL_1"
    GIT_BRANCH_ENV_VAR_NAME = "GIT_BRANCH"
    GIT_COMMIT_ENV_VAR_NAME = "GIT_COMMIT"
    JOB_NAME_ENV_VAR_NAME = "JOB_NAME"
    BUILD_ID_ENV_VAR_NAME = "BUILD_ID"
    environment_info = None


    @staticmethod
    def get_test_run_id(repo_url, commit_hash):
        pass # TODO


    @classmethod
    def _build_env_info(cls):
        try:
            repo_url = os.getenv(cls.GIT_URL_ENV_VAR_NAME)
            if not repo_url:
                repo_url = os.getenv(cls.GIT_URL_1_ENV_VAR_NAME)
            
            repo_name = GitHelper.extractRepoName(repo_url)
            branch = os.getenv(cls.GIT_BRANCH_ENV_VAR_NAME)
            commit_hash = os.getenv(cls.GIT_COMMIT_ENV_VAR_NAME)
            commit_message = GitHelper.get_commit_message()

            if not branch:
                branch = GitHelper.get_branch()

            if not commit_hash:
                commit_hash = GitHelper.get_commit_hash()

            test_run_id = cls.get_test_run_id(repo_url, commit_hash)

            cls.environment_info = EnvironmentInfo(test_run_id, cls.ENVIRONMENT, repo_url, repo_name, 
                branch, commit_hash, commit_message)
        except Exception as err:
            LOGGER.error("Unable to build environment info", err)
            cls.environment_info = None

JenkinsEnvironmentInfoProvider._build_env_info()
