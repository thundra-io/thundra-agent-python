import abc
from thundra.constants import (TEST_RUN_EVENTS_DATA_VERSION,
     DATA_FORMAT_VERSION,
     THUNDRA_AGENT_VERSION)
from thundra.config.config_provider import ConfigProvider
from thundra.config.config_names import THUNDRA_APIKEY


ABC = abc.ABCMeta('ABC', (object,), {})

class TestRunMonitoring(ABC):

    TEST_RUN_DATA_MODEL_VERSION = TEST_RUN_EVENTS_DATA_VERSION
    DATA_FORMAT_VERSION = DATA_FORMAT_VERSION
    AGENT_VERSION = THUNDRA_AGENT_VERSION

    def get_monitoring_data(self):
        return {
            'apiKey': ConfigProvider.get(THUNDRA_APIKEY, None),
            'type': None,
            'dataModelVersion': self.DATA_FORMAT_VERSION,
            'data': None
        }