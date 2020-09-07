import simplejson as json
import logging
import concurrent.futures as futures

from thundra.plugins.log.thundra_logger import debug_logger
from thundra import constants, composite, utils
from thundra.config.config_provider import ConfigProvider
from thundra.config import config_names

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

    def send_report(self, reports):
        if not self.api_key:
            debug_logger("API key not set, not sending report to Thundra.")
            return []

        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'ApiKey ' + self.api_key
        }
        rest_composite_data_enabled = ConfigProvider.get(config_names.THUNDRA_REPORT_REST_COMPOSITE_ENABLE, True)
        path = constants.COMPOSITE_DATA_PATH if rest_composite_data_enabled else constants.PATH

        request_url = "https://" + utils.get_nearest_collector() + "/v1" + path
        base_url = ConfigProvider.get(config_names.THUNDRA_REPORT_REST_BASEURL)
        if base_url is not None:
            request_url = base_url + path

        if ConfigProvider.get(config_names.THUNDRA_REPORT_CLOUDWATCH_ENABLE):
            if ConfigProvider.get(config_names.THUNDRA_REPORT_CLOUDWATCH_COMPOSITE_ENABLE, True):
                reports_json = self.prepare_composite_report_json(reports)
                for report in reports_json:
                    print(report)
            else:
                for report in reports:
                    try:
                        print(json.dumps(report, separators=(',', ':')))
                    except TypeError:
                        logger.error(("Couldn't dump report with type {} to json string, "
                                      "probably it contains a byte array").format(report.get('type')))

            return []

        if rest_composite_data_enabled:
            reports_json = self.prepare_composite_report_json(reports)
        else:
            reports_json = self.prepare_report_json(reports)

        responses = []
        if len(reports_json) > 0:
            _futures = [self.pool.submit(self.send_batch, (request_url, headers, data)) for data in reports_json]
            responses = [future.result() for future in futures.as_completed(_futures)]

        if ConfigProvider.get(config_names.THUNDRA_DEBUG_ENABLE):
            debug_logger("Thundra API responses: " + str(responses))
        return responses

    def send_batch(self, args):
        url, headers, data = args
        return self.session.post(url, data=data, headers=headers, timeout=constants.DEFAULT_REPORT_TIMEOUT)

    def get_report_batches(self, reports):
        batch_size = ConfigProvider.get(config_names.THUNDRA_REPORT_REST_COMPOSITE_BATCH_SIZE)
        if ConfigProvider.get(config_names.THUNDRA_REPORT_CLOUDWATCH_ENABLE):
            batch_size = ConfigProvider.get(config_names.THUNDRA_REPORT_CLOUDWATCH_COMPOSITE_BATCH_SIZE)

        batches = [reports[i:i + batch_size] for i in range(0, len(reports), batch_size)]
        return batches

    def prepare_report_json(self, reports):
        batches = self.get_report_batches(reports)
        batched_reports = []
        for batch in batches:
            report_jsons = []
            for report in batch:
                try:
                    report_jsons.append(json.dumps(report, separators=(',', ':')))
                except TypeError:
                    logger.error(("Couldn't dump report with type {} to json string, "
                                  "probably it contains a byte array").format(report.get('type')))
            json_string = "[{}]".format(','.join(report_jsons))
            batched_reports.append(json_string)
        return batched_reports

    def prepare_composite_report_json(self, reports):
        invocation_report = None
        for report in reports:
            if report["type"] == "Invocation":
                invocation_report = report

        if not invocation_report:
            return []

        common_fields = composite.init_composite_data_common_fields(invocation_report["data"])

        batches = self.get_report_batches(reports)
        batched_reports = []

        for batch in batches:
            all_monitoring_data = [composite.remove_common_fields(report["data"]) for report in batch]
            composite_data = composite.get_composite_data(all_monitoring_data, self.api_key, common_fields)
            try:
                batched_reports.append(json.dumps(composite_data, separators=(',', ':')))

            except TypeError:
                logger.error("Couldn't dump report with type Composite to json string, "
                             "probably it contains a byte array")

        return batched_reports
