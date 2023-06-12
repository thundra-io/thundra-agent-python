import logging
import concurrent.futures as futures

from catchpoint.plugins.log.catchpoint_logger import debug_logger
from catchpoint import constants, utils
from catchpoint.config.config_provider import ConfigProvider
from catchpoint.config import config_names
from catchpoint.encoder import to_json

try:
    import requests
except ImportError:
    from botocore.vendored import requests

logger = logging.getLogger(__name__)


class Reporter:

    def __init__(self, api_key, session=None):
        if api_key is not None:
            self.api_key = api_key
        else:
            self.api_key = ''
            logger.error('Please set an API key!')

        if not session:
            session = requests.Session()
            adapter = requests.adapters.HTTPAdapter(pool_maxsize=20)
            session.mount("https://", adapter)

        self.session = session
        self.pool = futures.ThreadPoolExecutor(max_workers=20)

    def send_reports(self, reports, **opts):
        if not self.api_key:
            debug_logger("API key not set, not sending report to Catchpoint.")
            return []

        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'ApiKey ' + self.api_key
        }

        base_url = self.get_collector_url()
        request_url = base_url + constants.PATH

        reports_json = self.prepare_report_json(reports)
        responses = []
        if len(reports_json) > 0:
            _futures = [self.pool.submit(self.send_batch, (request_url, headers, data)) for data in reports_json]
            responses = [future.result() for future in futures.as_completed(_futures)]

        if ConfigProvider.get(config_names.CATCHPOINT_DEBUG_ENABLE):
            debug_logger("Catchpoint API responses: " + str(responses))
        return responses

    def send_batch(self, args):
        url, headers, data = args
        return self.session.post(url, data=data, headers=headers, timeout=constants.DEFAULT_REPORT_TIMEOUT)

    def get_report_batches(self, reports):
        batch_size = ConfigProvider.get(config_names.CATCHPOINT_REPORT_REST_COMPOSITE_BATCH_SIZE)
        batches = [reports[i:i + batch_size] for i in range(0, len(reports), batch_size)]
        return batches


    def prepare_report_json(self, reports):
        batches = self.get_report_batches(reports)
        batched_reports = []
        for batch in batches:
            report_jsons = []
            for report in batch:
                try:
                    report_jsons.append(to_json(report, separators=(',', ':')))
                except TypeError:
                    logger.error(("Couldn't dump report with type {} to json string, "
                                  "probably it contains a byte array").format(report.get('type')))
            json_string = "[{}]".format(','.join(report_jsons))
            batched_reports.append(json_string)
        return batched_reports


    @staticmethod
    def get_collector_url():
        use_local = ConfigProvider.get(config_names.CATCHPOINT_REPORT_REST_LOCAL)

        if use_local:
            return 'http://' + constants.LOCAL_COLLECTOR_ENDPOINT + '/v1'
        return ConfigProvider.get(config_names.CATCHPOINT_REPORT_REST_BASEURL, 'https://' + utils.get_nearest_collector() + '/v1')

