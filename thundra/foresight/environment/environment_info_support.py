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
    def init(cls):
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
    def set_span_tags(cls, span):
        """Set span and invocation data tags corresponds to TestRunner

        Args:
            obj (ThundraSpan | invocation): Span or invocation data
        """
        if cls.environment_info:
            span.set_tag(TestRunnerTags.TEST_ENVIRONMENT, cls.environment_info.environment)
            span.set_tag(TestRunnerTags.SOURCE_CODE_REPO_URL, cls.environment_info.repo_url)
            span.set_tag(TestRunnerTags.SOURCE_CODE_REPO_NAME, cls.environment_info.repo_name)
            span.set_tag(TestRunnerTags.SOURCE_CODE_BRANCH, cls.environment_info.branch)
            span.set_tag(TestRunnerTags.SOURCE_CODE_COMMIT_HASH, cls.environment_info.commit_hash)
            span.set_tag(TestRunnerTags.SOURCE_CODE_COMMIT_MESSAGE, cls.environment_info.commit_message)

    @classmethod
    def set_invocation_tags(cls, invocation_data):
        """Set span and invocation data tags corresponds to TestRunner

        Args:
            obj (ThundraSpan | invocation): Span or invocation data
        """
        if cls.environment_info:
            invocation_data[TestRunnerTags.TEST_ENVIRONMENT] =  cls.environment_info.environment
            invocation_data[TestRunnerTags.SOURCE_CODE_REPO_URL] =  cls.environment_info.repo_url
            invocation_data[TestRunnerTags.SOURCE_CODE_REPO_NAME] =  cls.environment_info.repo_name
            invocation_data[TestRunnerTags.SOURCE_CODE_BRANCH] =  cls.environment_info.branch
            invocation_data[TestRunnerTags.SOURCE_CODE_COMMIT_HASH] =  cls.environment_info.commit_hash
            invocation_data[TestRunnerTags.SOURCE_CODE_COMMIT_MESSAGE] =  cls.environment_info.commit_message