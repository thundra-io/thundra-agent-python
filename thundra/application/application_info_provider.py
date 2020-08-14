import abc

from thundra.config import config_names
from thundra.config.config_provider import ConfigProvider

ABC = abc.ABCMeta('ABC', (object,), {})


class ApplicationInfoProvider(ABC):

    @abc.abstractmethod
    def get_application_info(self):
        pass

    @staticmethod
    def parse_application_tags():
        application_tags = {}
        prefix_length = len(config_names.THUNDRA_APPLICATION_TAG_PREFIX)
        for key in ConfigProvider.configs:
            if key.startswith(config_names.THUNDRA_APPLICATION_TAG_PREFIX):
                app_tag_key = key[prefix_length:]
                val = ConfigProvider.get(key)
                application_tags[app_tag_key] = val
        return application_tags
