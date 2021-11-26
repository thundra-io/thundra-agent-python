from foresight.model.test_run_result import TestRunResult
from foresight.model.test_run_monitoring import TestRunMonitoring

class TestRunStatus(TestRunResult, TestRunMonitoring):

    EVENT_NAME="TestRunStatus"

    def __init__(self, id=None, project_id=None, task_id=None, total_count=0, successful_count=0, 
        failed_count=0, ignored_count=0, aborted_count=0, start_timestamp=None, status_timestamp=None,
        host_name=None, environment_info=None, tags=None):
        super(TestRunStatus, self).__init__(total_count, successful_count, failed_count,
            ignored_count, aborted_count)
        self.id = id
        self.project_id = project_id
        self.task_id = task_id
        self.start_timestamp = start_timestamp
        self.status_timestamp = status_timestamp
        self.host_name = host_name
        if environment_info != None:
            self.environment = environment_info.environment if environment_info.environment else None
            self.repo_url = environment_info.repo_url if environment_info.repo_url else None
            self.repo_name = environment_info.repo_name if environment_info.repo_name else None
            self.branch = environment_info.branch if environment_info.branch else None
            self.commit_hash = environment_info.commit_hash if environment_info.commit_hash else None
            self.commit_message = environment_info.commit_message if environment_info.commit_message else None
        else:
            self.environment = None
            self.repo_url = None
            self.repo_name = None
            self.branch = None
            self.commit_hash = None
            self.commit_message = None
        self.tags = tags

    def to_json(self):
        return {
            "id": self.id,
            "projectId": self.project_id,
            "taskId": self.task_id,
            "type": self.EVENT_NAME,
            "agentVersion": self.AGENT_VERSION,
            "dataModelVersion": self.TEST_RUN_DATA_MODEL_VERSION,
            "totalCount" : self.total_count,
            "successfulCount" : self.successful_count,
            "failedCount" : self.failed_count,
            "ignoredCount" : self.ignored_count,
            "abortedCount" : self.aborted_count,
            "startTimestamp" : self.start_timestamp,
            "statusTimestamp" : self.status_timestamp,
            "environment": self.environment,
            "repoURL": self.repo_url,
            "repoName": self.repo_name,
            "branch": self.branch,
            "commitHash": self.commit_hash,
            "commitMessage": self.commit_message,
            "tags": self.tags
        }
    def get_monitoring_data(self):
        monitoring_data = super().get_monitoring_data()
        monitoring_data["type"] = self.EVENT_NAME
        monitoring_data["data"] = self.to_json()
        return monitoring_data  