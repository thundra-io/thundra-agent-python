
class TestRunFinish:

    def __init__(self, id, project_id, task_id, total_count, successful_count, 
        failed_count, ignored_count, aborted_count, start_timestamp, finish_timestamp,
        duration, host_name, environment_info, tags):
        self.id = id
        self.project_id = project_id
        self.task_id = task_id
        self.total_count = total_count
        self.successful_count = successful_count
        self.failed_count = failed_count
        self.ignored_count = ignored_count
        self.aborted_count = aborted_count
        self.start_timestamp = start_timestamp
        self.finish_timestamp = finish_timestamp
        self.duration = duration
        self.host_name = host_name
        self.environment = environment_info.environment if environment_info.environment else None
        self.repo_url = environment_info.repo_url if environment_info.repo_url else None
        self.repo_name = environment_info.repo_name if environment_info.repo_name else None
        self.branch = environment_info.branch if environment_info.branch else None
        self.commit_hash = environment_info.commit_hash if environment_info.commit_hash else None
        self.commit_message = environment_info.commit_message if environment_info.commit_message else None
        self.tags = tags

    def to_json(self):
        return {
            "id": self.id,
            "projectId'": self.project_id,
            "taskId'": self.task_id,
            "totalCount" : self.total_count,
            "successfulCount" : self.successful_count,
            "failedCount" : self.failed_count,
            "ignoredCount" : self.ignored_count,
            "abortedCount" : self.aborted_count,
            "startTimestamp" : self.start_timestamp,
            "finishTimestamp" : self.finish_timestamp,
            "duration" : self.duration,
            "environment": self.environment,
            "repoURL": self.repo_url,
            "repoName": self.repo_name,
            "branch": self.branch,
            "commitHash": self.commit_hash,
            "commitMessage": self.commit_message,
            "tags": self.tags
        }