import logging
from thundra.foresight.environment.github.github_environment_info_provider import GithubEnvironmentInfoProvider
from thundra.foresight.environment.git.git_helper import GitHelper
from thundra.foresight.environment.environment_info import EnvironmentInfo

LOGGER = logging.getLogger(__name__)

class GitEnvironmentInfoProvider:
    
    ENVIRONMENT = "Git"
    environment_info = None

    @staticmethod
    def get_test_run_id(repo_name, commit_hash):
        pass # TODO

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
            test_run_id = cls.get_test_run_id(repo_name, commit_hash)
            cls.environment_info = EnvironmentInfo(test_run_id, cls.ENVIRONMENT, repo_url, repo_name,
                branch, commit_hash, commit_message)
        except Exception as err:
            LOGGER.error("Unable to build environment info", err)
            cls.environment_info = None

GithubEnvironmentInfoProvider._build_env_info()