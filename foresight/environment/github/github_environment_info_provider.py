from foresight.environment.git.git_helper import GitHelper
from foresight.environment.environment_info import EnvironmentInfo
from foresight.utils.test_runner_utils import TestRunnerUtils
import json, os, logging
from foresight.utils.generic_utils import print_debug_message_to_console


LOGGER = logging.getLogger(__name__)


class GithubEnvironmentInfoProvider:
    ENVIRONMENT = "GitHub"
    GITHUB_REPOSITORY_ENV_VAR_NAME = "GITHUB_REPOSITORY"
    GITHUB_HEAD_REF_ENV_VAR_NAME = "GITHUB_HEAD_REF"
    GITHUB_REF_ENV_VAR_NAME = "GITHUB_REF"
    GITHUB_EVENT_PATH_ENV_VAR_NAME = "GITHUB_EVENT_PATH"
    GITHUB_SHA_ENV_VAR_NAME = "GITHUB_SHA"
    GITHUB_RUN_ID_ENV_VAR_NAME = "GITHUB_RUN_ID"
    INVOCATION_ID_ENV_VAR_NAME = "INVOCATION_ID"
    REFS_HEADS_PREFIX = "refs/heads/"

    @classmethod
    def get_test_run_id(cls, repo_url, commit_hash):
        configured_test_run_id = TestRunnerUtils.get_configured_test_run_id()
        if configured_test_run_id:
            return configured_test_run_id
        run_id = os.getenv(cls.GITHUB_RUN_ID_ENV_VAR_NAME)
        if run_id:
            test_run_key = run_id
            invocation_id = os.getenv(cls.INVOCATION_ID_ENV_VAR_NAME)
            if invocation_id:
                test_run_key = TestRunnerUtils.string_concat_by_underscore(run_id, invocation_id)
            return TestRunnerUtils.get_test_run_id(cls.ENVIRONMENT, repo_url, commit_hash, 
                test_run_key)
        else:
            return TestRunnerUtils.get_default_test_run_id(cls.ENVIRONMENT, repo_url, commit_hash)


    @classmethod
    def build_env_info(cls):
        try:
            github_repo = os.getenv(cls.GITHUB_REPOSITORY_ENV_VAR_NAME)
            repo_url = "https://github.com/" + github_repo + ".git"
            repo_name = GitHelper.extractRepoName(github_repo)
            branch = os.getenv(cls.GITHUB_HEAD_REF_ENV_VAR_NAME)
            commit_hash = os.getenv(cls.GITHUB_SHA_ENV_VAR_NAME)
            commit_message = GitHelper.get_commit_message()
            github_event_path = os.getenv(cls.GITHUB_EVENT_PATH_ENV_VAR_NAME)
            if github_event_path:
                try:
                    if os.path.isfile(github_event_path):
                        with open(github_event_path) as f:
                            try:
                                event_data = json.loads(f.read())
                                from jsonpath_ng import jsonpath, parse
                                jsonpath_expression = parse('$.pull_request.head.sha')
                                match = jsonpath_expression.find(event_data)
                                commit_hash = match[0].value
                            except Exception as err:
                                LOGGER.error("Github Unable to get json data from  GitHub event file " + github_event_path);
                except Exception as err:
                    print_debug_message_to_console("Unable to read GitHub event from file " + github_event_path)
                    LOGGER.error("Github Unable to read GitHub event from file " + github_event_path)
                    pass

            if not branch:
                branch = os.getenv(cls.GITHUB_REF_ENV_VAR_NAME)
                if branch and branch.startswith(cls.REFS_HEADS_PREFIX):
                    branch = branch[len(cls.REFS_HEADS_PREFIX):]

            if not branch:
                branch = GitHelper.get_branch()

            if not commit_hash:
                commit_hash = GitHelper.get_commit_hash()
            
            test_run_id = cls.get_test_run_id(repo_url, commit_hash)
            env_info = EnvironmentInfo(test_run_id, cls.ENVIRONMENT, repo_url, repo_name, branch, commit_hash, commit_message)
            print_debug_message_to_console("Github Environment info: {}".format(env_info.to_json()))
            return env_info
        except Exception as err:
            print_debug_message_to_console("Github Unable to build environment info: {}".format(err))
            LOGGER.error("Github Unable to build environment info: {}".format(err))
            pass
        return None