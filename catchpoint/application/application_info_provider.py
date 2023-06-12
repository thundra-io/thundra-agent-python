import abc, sys

from catchpoint.config import config_names
from catchpoint.config.config_provider import ConfigProvider

ABC = abc.ABCMeta('ABC', (object,), {})


class ApplicationInfoProvider(ABC):
    
    APPLICATION_RUNTIME = "python"
    APPLICATION_RUNTIME_VERSION = str(sys.version_info[0])

    @abc.abstractmethod
    def get_application_info(self):
        pass

    @staticmethod
    def parse_application_tags():
        application_tags = {}
        prefix_length = len(config_names.CATCHPOINT_APPLICATION_TAG_PREFIX) + 1
        for key in ConfigProvider.configs:
            if key.startswith(config_names.CATCHPOINT_APPLICATION_TAG_PREFIX) and len(key) >= prefix_length:
                app_tag_key = key[prefix_length:]
                val = ConfigProvider.get(key)
                application_tags[app_tag_key] = val
        return application_tags
