from thundra.application.global_application_info_provider import GlobalApplicationInfoProvider


class ApplicationManager:
    application_info_provider = None

    @staticmethod
    def set_application_info_provider(application_info_provider):
        ApplicationManager.application_info_provider = GlobalApplicationInfoProvider(application_info_provider)

    @staticmethod
    def get_application_info_provider():
        return ApplicationManager.application_info_provider

    @staticmethod
    def get_application_info():
        return ApplicationManager.application_info_provider.get_application_info()
