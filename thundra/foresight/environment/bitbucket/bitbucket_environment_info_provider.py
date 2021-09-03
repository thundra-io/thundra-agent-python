from thundra.foresight.environment.git.git_helper import GitHelper
from thundra.foresight.environment.environment_info import EnvironmentInfo
import os, logging

LOGGER = logging.getLogger(__name__)

class BitbucketEnvironmentInfoProvider:

    ENVIRONMENT = "BitBucket"
    BITBUCKET_GIT_HTTP_ORIGIN_ENV_VAR_NAME = "BITBUCKET_GIT_HTTP_ORIGIN"
    BITBUCKET_GIT_SSH_ORIGIN_ENV_VAR_NAME = "BITBUCKET_GIT_SSH_ORIGIN"
    BITBUCKET_BRANCH_ENV_VAR_NAME = "BITBUCKET_BRANCH"
    BITBUCKET_COMMIT_ENV_VAR_NAME = "BITBUCKET_COMMIT"
    BITBUCKET_BUILD_NUMBER_ENV_VAR_NAME = "BITBUCKET_BUILD_NUMBER"
    environment_info = None

    @staticmethod
    def get_test_run_id(repo_url, commit_hash):
        pass #TODO

    @classmethod
    def _build_env_info(cls):
        try:
            repo_url = os.getenv(cls.BITBUCKET_GIT_HTTP_ORIGIN_ENV_VAR_NAME)
            if not repo_url:
                repo_url = os.getenv(cls.BITBUCKET_GIT_SSH_ORIGIN_ENV_VAR_NAME)
            repo_name = GitHelper.extractRepoName(repo_url)
            branch = os.getenv(cls.BITBUCKET_BRANCH_ENV_VAR_NAME)
            commit_hash = os.getenv(cls.BITBUCKET_COMMIT_ENV_VAR_NAME)
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

BitbucketEnvironmentInfoProvider._build_env_info()