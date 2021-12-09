from foresight.environment.git.git_helper import GitHelper
from foresight.environment.environment_info import EnvironmentInfo
from foresight.utils.test_runner_utils import TestRunnerUtils
import os, logging
from foresight.utils.generic_utils import print_debug_message_to_console

LOGGER = logging.getLogger(__name__)

class CodebuildEnvironmentInfoProvider:
    ENVIRONMENT = "CircleCI" # TODO Change it CodeBuild after foresight backend fixed.
    CODEBUILD_GITHUB_REPOSITORY_URL_ENV_VAR_NAME = "CODEBUILD_SOURCE_REPO_URL"
    CODEBUILD_REPOSITORY_URL_ENV_VAR_NAME = "CODEBUILD_SRC_DIR"
    CODEBUILD_BRANCH_ENV_VAR_NAME = "CODEBUILD_SOURCE_VERSION"
    CODEBUILD_RESOLVED_SOURCE_VERSION_ENV_VAR_NAME = "CODEBUILD_RESOLVED_SOURCE_VERSION"
    CODEBUILD_BUILD_ID_ENV_VAR_NAME = "CODEBUILD_BUILD_ID"
    CODEBUILD_BUILD_NUM_ENV_VAR_NAME = "CODEBUILD_BUILD_NUMBER"
    CODEBUILD_COMMIT_MESSAGE_ENV_VAR_NAME = "CODEBUILD_COMMIT_MESSAGE"
    CODEBUILD_GIT_COMMIT_MESSAGE_ENV_VAR_NAME = "CODEBUILD_GIT_MESSAGE" # https://github.com/thii/aws-codebuild-extras
    CODEBUILD_GIT_HASH_ENV_VAR_NAME = "CODEBUILD_GIT_COMMIT"
    CODEBUILD_GIT_BRANCH_ENV_VAR_NAME = "CODEBUILD_GIT_BRANCH"


    @classmethod
    def get_test_run_id(cls, repo_url, commit_hash):
        configured_test_run_id = TestRunnerUtils.get_configured_test_run_id()
        if configured_test_run_id:
            return configured_test_run_id
        build_id = os.getenv(cls.CODEBUILD_BUILD_ID_ENV_VAR_NAME)
        build_num = os.getenv(cls.CODEBUILD_BUILD_NUM_ENV_VAR_NAME)
        test_run_key = TestRunnerUtils.string_concat_by_underscore(build_id, build_num)
        if test_run_key != "":
            return TestRunnerUtils.get_test_run_id(cls.ENVIRONMENT, repo_url, commit_hash,
                test_run_key)
        else:
            return TestRunnerUtils.get_default_test_run_id(cls.ENVIRONMENT, repo_url, commit_hash)
            

    @classmethod
    def build_env_info(cls):
        try:
            repo_url = os.getenv(cls.CODEBUILD_GITHUB_REPOSITORY_URL_ENV_VAR_NAME) or os.getenv(cls.CODEBUILD_REPOSITORY_URL_ENV_VAR_NAME)
            if repo_url == None or repo_url.startswith('s3://'):
                LOGGER.info("Unsupported repo_url for Codebuild: {}".format(repo_url))
                return
            repo_name = GitHelper.extractRepoName(repo_url)
            branch = os.getenv(cls.CODEBUILD_GIT_BRANCH_ENV_VAR_NAME) or os.getenv(cls.CODEBUILD_BRANCH_ENV_VAR_NAME)
            commit_hash = os.getenv(cls.CODEBUILD_GIT_HASH_ENV_VAR_NAME) or os.getenv(cls.CODEBUILD_RESOLVED_SOURCE_VERSION_ENV_VAR_NAME)
            commit_message = os.getenv(cls.CODEBUILD_COMMIT_MESSAGE_ENV_VAR_NAME) or os.getenv(cls.CODEBUILD_GIT_COMMIT_MESSAGE_ENV_VAR_NAME)

            if not branch:
                branch = GitHelper.get_branch()

            if not commit_hash:
                commit_hash = GitHelper.get_commit_hash()

            test_run_id = cls.get_test_run_id(repo_url, commit_hash)

            env_info = EnvironmentInfo(test_run_id, cls.ENVIRONMENT, repo_url, repo_name, branch, 
                commit_hash, commit_message)
            print_debug_message_to_console("CodeBuild Environment info: {}".format(env_info.to_json()))
            return env_info
        except Exception as err:
            print_debug_message_to_console("CodeBuild Unable to build environment info: {}".format(err))
            LOGGER.error("CodeBuild Unable to build environment info: {}".format(err))
            pass
        return None