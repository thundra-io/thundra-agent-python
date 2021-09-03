from thundra.foresight.environment.git.git_helper import GitHelper
from thundra.foresight.environment.environment_info import EnvironmentInfo
import os, logging


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
    environment_info = None

    @staticmethod
    def get_test_run_id(repo_url, commit_hash):
        pass #TODO

    @classmethod
    def _build_env_info(cls):
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
            
            cls.environment_info = EnvironmentInfo(test_run_id, cls.ENVIRONMENT, repo_url, 
                repo_name, branch, commit_hash, commit_message)
        except Exception as err:
            LOGGER.error("Unable to build environment info", err)
            cls.environment_info = None

TravisCIEnvironmentInfoProvider._build_env_info()