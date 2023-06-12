from catchpoint.application.application_info_provider import ApplicationInfoProvider
from catchpoint.config import config_names
from catchpoint.config.config_provider import ConfigProvider


class GlobalApplicationInfoProvider(ApplicationInfoProvider):
    def __init__(self, application_info_provider=None):
        self.application_info = {}
        self.application_info_provider = application_info_provider
        if self.application_info_provider:
            self.application_info = self.application_info_provider.get_application_info()

        app_info_from_config = self.get_application_info_from_config()

        self.update(app_info_from_config)

    def get_application_info(self):
        return self.application_info

    def get_application_tags(self):
        return self.application_info.get('applicationTags', {}).copy()

    @staticmethod
    def get_application_info_from_config():
        return {
            'applicationId': ConfigProvider.get(config_names.CATCHPOINT_APPLICATION_ID),
            'applicationInstanceId': ConfigProvider.get(config_names.CATCHPOINT_APPLICATION_INSTANCE_ID),
            'applicationDomainName': ConfigProvider.get(config_names.CATCHPOINT_APPLICATION_DOMAIN_NAME),
            'applicationClassName': ConfigProvider.get(config_names.CATCHPOINT_APPLICATION_CLASS_NAME),
            'applicationName': ConfigProvider.get(config_names.CATCHPOINT_APPLICATION_NAME),
            'applicationVersion': ConfigProvider.get(config_names.CATCHPOINT_APPLICATION_VERSION, ''),
            'applicationStage': ConfigProvider.get(config_names.CATCHPOINT_APPLICATION_STAGE, ''),
            'applicationRegion': ConfigProvider.get(config_names.CATCHPOINT_APPLICATION_REGION, ''),
            'applicationRuntime': ApplicationInfoProvider.APPLICATION_RUNTIME,
            'applicationRuntimeVersion': ApplicationInfoProvider.APPLICATION_RUNTIME_VERSION,
            'applicationTags': ApplicationInfoProvider.parse_application_tags()
        }

    def update(self, opts):
        filtered_opts = {k: v for k, v in opts.items() if v is not None}
        self.application_info.update(filtered_opts)
