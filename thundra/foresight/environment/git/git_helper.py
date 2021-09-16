import __future__
import os
import logging
from thundra.foresight.environment.git.utils import backward_search_for_file
from git import Repo

LOGGER = logging.getLogger(__name__)

class GitHelper:

    USER_DIR = os.getcwd()
    SOURCE_CODE_PATH = "sourceCodePath"
    REPOSITORY_URL = "repositoryURL"
    COMMIT_HASH = "commitHash"
    COMMIT_MESSAGE = "commitMessage"
    BRANCH = "branch"
    GIT_FOLDER_NAME = ".git"
    git_info_map = dict()

    @classmethod
    def get_source_root_path(cls):
        return cls.git_info_map.get(GitHelper.SOURCE_CODE_PATH, None)

    @classmethod
    def get_repo_url(cls):
        return cls.git_info_map.get(GitHelper.REPOSITORY_URL, None)

    @classmethod
    def get_branch(cls):
        return cls.git_info_map.get(GitHelper.BRANCH, None)

    @classmethod
    def get_commit_hash(cls):
        return cls.git_info_map.get(GitHelper.COMMIT_HASH, None)

    @classmethod
    def get_commit_message(cls):
        return cls.git_info_map.get(GitHelper.COMMIT_MESSAGE, None)


    @classmethod
    def populate_git_info_map(cls):
        git_folder_path = backward_search_for_file(cls.USER_DIR, cls.GIT_FOLDER_NAME)
        if not git_folder_path:
            LOGGER.error("Could not locate " + cls.USER_DIR + " starting from user.dir: " + cls.GIT_FOLDER_NAME)
            return {}
        try:
            git_repo = Repo(git_folder_path)
            active_branch = git_repo.active_branch
            commit_hash = str(active_branch.commit)
            commit_message = active_branch.commit.message
            repo_url = git_repo.remotes[0].config_reader.get("url")
            source_code_path = git_repo.working_dir
            cls.git_info_map[GitHelper.SOURCE_CODE_PATH] = source_code_path
            cls.git_info_map[GitHelper.BRANCH] = active_branch
            cls.git_info_map[GitHelper.COMMIT_HASH] = commit_hash
            cls.git_info_map[GitHelper.COMMIT_MESSAGE] = commit_message
            cls.git_info_map[GitHelper.REPOSITORY_URL] = repo_url
        except Exception as err:
            raise err # TODO


    @staticmethod
    def normalize_repo_name(repo_name):
        if not repo_name:
            return None
        index = repo_name.index(".")
        if index >= 0:
            repo_name = repo_name[:index]
        return repo_name

    @staticmethod
    def extractRepoName(repo_url):
        if not repo_url:
            return None
        index = repo_url.rfind("/")
        if (index >= 0):
            return GitHelper.normalize_repo_name(repo_url[:index+1])
        else:
            return GitHelper.normalize_repo_name(repo_url)

# TODO
GitHelper.git_info_map = {
    "sourceCodePath": "sourceCodePath",
    "repositoryURL": "git@github.com:jaredpar/VsVim.git",
    "branch": "branch",
    "commitHash": "commitHash",
    "commitMessage": "commitMessage"
}
# GitHelper.populate_git_info_map()