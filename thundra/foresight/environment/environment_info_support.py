import os, logging
from thundra.foresight.environment.git.git_helper import GitHelper
from thundra.foresight.environment.git.git_env_info_provider import GitEnvironmentInfoProvider
from thundra.foresight.environment.github.github_environment_info_provider import GithubEnvironmentInfoProvider
from thundra.foresight.environment.gitlab.gitlab_environment_info_provider import GitlabEnvironmentInfoProvider
from thundra.foresight.environment.jenkins.jenkins_environment_info_provider import JenkinsEnvironmentInfoProvider
from thundra.foresight.environment.travisci.travisci_environment_info_provider import TravisCIEnvironmentInfoProvider
from thundra.foresight.environment.circleci.circleci_environment_info_provider import CircleCIEnvironmentInfoProvider
from thundra.foresight.environment.bitbucket.bitbucket_environment_info_provider import BitbucketEnvironmentInfoProvider
from thundra.foresight.test_runner_tags import TestRunnerTags


LOGGER = logging.getLogger(__name__)

class EnvironmentSupport:

    ENVIRONMENTS_VARS = {
        "GITHUB_REPOSITORY": GithubEnvironmentInfoProvider,
        "GITLAB_CI": GitlabEnvironmentInfoProvider,
        "JENKINS_HOME": JenkinsEnvironmentInfoProvider,
        "JENKINS_URL": JenkinsEnvironmentInfoProvider,
        "TRAVIS": TravisCIEnvironmentInfoProvider,
        "CIRCLECI": CircleCIEnvironmentInfoProvider,
        "BITBUCKET_GIT_HTTP_ORIGIN": BitbucketEnvironmentInfoProvider,
        "BITBUCKET_GIT_SSH_ORIGIN": BitbucketEnvironmentInfoProvider
    }
    environment_info = None

    '''
        First check git provider, then iterate over ENVIRONMENTS_VARS dict.
    '''
    @classmethod
    def _set_global_env_info(cls):
        global ENVIRONMENTS_VARS
        try:
            if GitHelper.get_repo_url():
                GitEnvironmentInfoProvider.build_env_info()
                cls.environment_info = GitEnvironmentInfoProvider.environment_info
            else:
                for key, clz in cls.ENVIRONMENTS_VARS.items():
                    if os.getenv(key):
                        clz.build_env_info()
                        cls.environment_info = clz.environment_info
                        break
        except Exception as err:
            LOGGER.error("Environment Support environment_info could not set", err)
            cls.environment_info = None


    @classmethod
    def set_tags(cls, obj):
        """Set span and invocation data tags corresponds to TestRunner

        Args:
            obj (ThundraSpan | invocation): Span or invocation data
        """
        if cls.environmentInfo:
            obj.setTag(TestRunnerTags.TEST_ENVIRONMENT, cls.environmentInfo.environment)
            obj.setTag(TestRunnerTags.SOURCE_CODE_REPO_URL, cls.environmentInfo.repo_url)
            obj.setTag(TestRunnerTags.SOURCE_CODE_REPO_NAME, cls.environmentInfo.repo_name)
            obj.setTag(TestRunnerTags.SOURCE_CODE_BRANCH, cls.environmentInfo.branch)
            obj.setTag(TestRunnerTags.SOURCE_CODE_COMMIT_HASH, cls.environmentInfo.commit_hash)
            obj.setTag(TestRunnerTags.SOURCE_CODE_COMMIT_MESSAGE, cls.environmentInfo.commit_message)


EnvironmentSupport._set_global_env_info()