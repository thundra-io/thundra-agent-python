class ApplicationInfo:

    def __init__(self, application_id = None, application_instance_id = None, application_domain_name = None,
         application_class_name = None, application_name = None, application_version = None, 
         application_stage = None, application_runtime = None, 
         application_runtime_version = None, application_tags = None):
        
        self.application_id = application_id 
        self.application_instance_id = application_instance_id 
        self.application_domain_name = application_domain_name 
        self.application_class_name = application_class_name 
        self.application_name = application_name 
        self.application_version = application_version 
        self.application_stage = application_stage 
        self.application_runtime = application_runtime 
        self.application_runtime_version = application_runtime_version 
        self.applicationTags = application_tags

    def to_json(self):
        return {
            'applicationId': self.application_id,
            'applicationInstanceId': self.application_instance_id,
            'applicationDomainName': self.application_domain_name,
            'applicationClassName': self.application_class_name,
            'applicationName': self.application_name,
            'applicationVersion': self.application_version,
            'applicationStage': self.application_stage,
            'applicationRuntime': self.application_runtime,
            'applicationRuntimeVersion': self.application_runtime_version,
            'applicationTags': self.applicationTags
        }