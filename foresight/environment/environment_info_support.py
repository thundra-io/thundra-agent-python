import os, logging
from foresight.environment.git.git_helper import GitHelper
from foresight.environment.git.git_env_info_provider import GitEnvironmentInfoProvider
from foresight.environment.github.github_environment_info_provider import GithubEnvironmentInfoProvider
from foresight.environment.gitlab.gitlab_environment_info_provider import GitlabEnvironmentInfoProvider
from foresight.environment.jenkins.jenkins_environment_info_provider import JenkinsEnvironmentInfoProvider
from foresight.environment.travisci.travisci_environment_info_provider import TravisCIEnvironmentInfoProvider
from foresight.environment.circleci.circleci_environment_info_provider import CircleCIEnvironmentInfoProvider
from foresight.environment.bitbucket.bitbucket_environment_info_provider import BitbucketEnvironmentInfoProvider
from foresight.environment.azure.azure_environment_info_provider import AzureEnvironmentInfoProvider
from foresight.test_runner_tags import TestRunnerTags
from foresight.utils.generic_utils import print_debug_message_to_console

LOGGER = logging.getLogger(__name__)

class EnvironmentSupport:

    ENVIRONMENTS_VARS = {
        "GITHUB_ENV": GithubEnvironmentInfoProvider, # https://docs.github.com/en/actions/learn-github-actions/environment-variables
        "CI_PROJECT_ID": GitlabEnvironmentInfoProvider, # https://docs.gitlab.com/ee/ci/variables/predefined_variables.html
        "JENKINS_HOME": JenkinsEnvironmentInfoProvider, # https://e.printstacktrace.blog/jenkins-pipeline-environment-variables-the-definitive-guide/
        "JENKINS_URL": JenkinsEnvironmentInfoProvider, # https://e.printstacktrace.blog/jenkins-pipeline-environment-variables-the-definitive-guide/
        "TRAVIS": TravisCIEnvironmentInfoProvider, # https://docs.travis-ci.com/user/environment-variables/#default-environment-variables
        "CIRCLECI": CircleCIEnvironmentInfoProvider, # https://circleci.com/docs/2.0/env-vars/#built-in-environment-variables
        "BITBUCKET_GIT_HTTP_ORIGIN": BitbucketEnvironmentInfoProvider, # https://support.atlassian.com/bitbucket-cloud/docs/variables-and-secrets/
        "BITBUCKET_GIT_SSH_ORIGIN": BitbucketEnvironmentInfoProvider, # https://support.atlassian.com/bitbucket-cloud/docs/variables-and-secrets/
        "TF_BUILD": AzureEnvironmentInfoProvider # https://docs.microsoft.com/en-us/azure/devops/pipelines/build/variables?view=azure-devops&tabs=yaml
    }
    environment_info = None


    @classmethod
    def init(cls):
        """First check git provider, then iterate over ENVIRONMENTS_VARS dict.
        """
        try:
            LOGGER.debug("Checking ci environments...")
            for key, clz in cls.ENVIRONMENTS_VARS.items():
                LOGGER.debug("Current key, clz: {}, {}".format(key,clz))
                if os.getenv(key):
                    ei = clz.build_env_info()
                    if ei: 
                        cls.environment_info = ei
                        print_debug_message_to_console("Environment info: {}".format(cls.environment_info.to_json()))
                        print_debug_message_to_console("Founded key and class: {}, {}".format(key, clz))
                        break
            if cls.environment_info == None:
                if GitHelper.get_repo_url():
                    print_debug_message_to_console("Couldn't find any ci envrionment! Trying .git file...")
                    cls.environment_info = GitEnvironmentInfoProvider.build_env_info()
                    print_debug_message_to_console("Environment info: {}".format(cls.environment_info.to_json()))
                else:
                    print_debug_message_to_console("Couldn't find .git file!")
        except Exception as err:
            LOGGER.error("Environment Support environment_info could not set: {}".format(err))
            cls.environment_info = None
            print_debug_message_to_console("environment_info is None!")
            pass


    @classmethod
    def set_span_tags(cls, span):
        """Set span data tags corresponds to TestRunner

        Args:
            obj (ThundraSpan): Span or invocation data
        """
        try:
            if cls.environment_info:
                span.set_tag(TestRunnerTags.TEST_ENVIRONMENT, cls.environment_info.environment)
                span.set_tag(TestRunnerTags.SOURCE_CODE_REPO_URL, cls.environment_info.repo_url)
                span.set_tag(TestRunnerTags.SOURCE_CODE_REPO_NAME, cls.environment_info.repo_name)
                span.set_tag(TestRunnerTags.SOURCE_CODE_BRANCH, cls.environment_info.branch)
                span.set_tag(TestRunnerTags.SOURCE_CODE_COMMIT_HASH, cls.environment_info.commit_hash)
                span.set_tag(TestRunnerTags.SOURCE_CODE_COMMIT_MESSAGE, cls.environment_info.commit_message)
        except Exception as e:
            LOGGER.error("Couldn't set environment info for span tags.")
            pass


    @classmethod
    def set_invocation_tags(cls, invocation_data):
        """Set invocation data tags corresponds to TestRunner

        Args:
            obj (invocation): Span or invocation data
        """
        try:
            if cls.environment_info:
                invocation_data[TestRunnerTags.TEST_ENVIRONMENT] =  cls.environment_info.environment
                invocation_data[TestRunnerTags.SOURCE_CODE_REPO_URL] =  cls.environment_info.repo_url
                invocation_data[TestRunnerTags.SOURCE_CODE_REPO_NAME] =  cls.environment_info.repo_name
                invocation_data[TestRunnerTags.SOURCE_CODE_BRANCH] =  cls.environment_info.branch
                invocation_data[TestRunnerTags.SOURCE_CODE_COMMIT_HASH] =  cls.environment_info.commit_hash
                invocation_data[TestRunnerTags.SOURCE_CODE_COMMIT_MESSAGE] =  cls.environment_info.commit_message
        except Exception as e:
            LOGGER.error("Couldn't set environment info for invocation tags.")
            pass