import os, logging
from thundra.foresight.environment.environment_info import EnvironmentInfo
from thundra.foresight.environment.git.git_helper import GitHelper
from thundra.foresight.environment.git.git_env_info_provider import GitEnvironmentInfoProvider
from thundra.foresight.environment.github.github_environment_info_provider import GithubEnvironmentInfoProvider
from thundra.foresight.environment.gitlab.gitlab_environment_info_provider import GitlabEnvironmentInfoProvider
from thundra.foresight.environment.jenkins.jenkins_environment_info_provider import JenkinsEnvironmentInfoProvider
from thundra.foresight.environment.travisci.travisci_environment_info_provider import TravisCIEnvironmentInfoProvider
from thundra.foresight.environment.circleci.circleci_environment_info_provider import CircleCIEnvironmentInfoProvider
from thundra.foresight.environment.bitbucket.bitbucket_environment_info_provider import BitbucketEnvironmentInfoProvider

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
                cls.environment_inf = GitEnvironmentInfoProvider.environment_info
            else:
                for key, clz in cls.ENVIRONMENTS_VARS.items():
                    if os.getenv(key):
                        cls.environment_inf = clz.environment_info
                        break
        except Exception as err:
            LOGGER.error("Environment Support environment_info could not set", err)
            cls.environment_info = None


    @classmethod
    def tag_invocation(cls, invocation):
        pass #TODO


    @classmethod
    def tag_span(cls, span):
        pass #TODO


EnvironmentSupport._set_global_env_info()