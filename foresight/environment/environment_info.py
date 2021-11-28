class EnvironmentInfo:

    def __init__(self, test_run_id, environment=None, repo_url=None, repo_name=None, 
        branch=None, commit_hash=None, commit_message=None):
        
        self.test_run_id = test_run_id
        self.environment = environment
        self.repo_url = repo_url
        self.repo_name = repo_name
        self.branch = branch
        self.commit_hash = commit_hash
        self.commit_message = commit_message

    def to_json(self):
        return {
            "testRunId": self.test_run_id,
            "environment": self.environment,
            "repoURL": self.repo_url,
            "repoName": self.repo_name,
            "branch": self.branch,
            "commitHash": self.commit_hash,
            "commitMessage": self.commit_message
        }