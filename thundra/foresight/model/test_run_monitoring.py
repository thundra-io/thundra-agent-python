import abc
from thundra.constants import (TEST_RUN_EVENTS_DATA_VERSION,
     DATA_FORMAT_VERSION,
     THUNDRA_AGENT_VERSION)

ABC = abc.ABCMeta('ABC', (object,), {})


class TestRunMonitoring(ABC):

    TEST_RUN_DATA_MODEL_VERSION = TEST_RUN_EVENTS_DATA_VERSION
    DATA_FORMAT_VERSION = DATA_FORMAT_VERSION
    AGENT_VERSION = THUNDRA_AGENT_VERSION

    def get_monitoring_data(self, api_key):
        return {
            'apiKey': api_key,
            'type': None,
            'dataModelVersion': self.DATA_FORMAT_VERSION,
            'data': None
        }