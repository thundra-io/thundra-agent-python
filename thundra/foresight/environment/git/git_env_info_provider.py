import logging
from thundra.foresight.environment.git.git_helper import GitHelper
from thundra.foresight.environment.environment_info import EnvironmentInfo
from thundra.foresight.util.test_runner_utils import TestRunnerUtils

LOGGER = logging.getLogger(__name__)

class GitEnvironmentInfoProvider:
    
    ENVIRONMENT = "Git"
    environment_info = None

    @classmethod
    def get_test_run_id(cls, repo_url, commit_hash):
        configured_test_run_id = TestRunnerUtils.get_configured_test_run_id()
        if configured_test_run_id:
            return configured_test_run_id
        return TestRunnerUtils.get_test_run_id(cls.ENVIRONMENT, repo_url, commit_hash)

    @classmethod
    def _build_env_info(cls):
        try:
            repo_url = GitHelper.get_repo_url()
            if not repo_url:
                return None
            repo_name = GitHelper.extractRepoName(repo_url)
            branch = GitHelper.get_branch()
            commit_hash = GitHelper.get_commit_hash()
            commit_message = GitHelper.get_commit_message()
            test_run_id = cls.get_test_run_id(repo_url, commit_hash)
            cls.environment_info = EnvironmentInfo(test_run_id, cls.ENVIRONMENT, repo_url, repo_name,
                branch, commit_hash, commit_message)
        except Exception as err:
            LOGGER.error("Unable to build environment info", err)
            cls.environment_info = None

GitEnvironmentInfoProvider._build_env_info()