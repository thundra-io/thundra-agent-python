import json
import logging

from thundra import constants, config, composite
from multiprocessing.dummy import Pool as ThreadPool

try:
    import requests
except ImportError:
    from botocore.vendored import requests

logger = logging.getLogger(__name__)


class Reporter():

    def __init__(self, api_key, session=None):
        if api_key is not None:
            self.api_key = api_key
        else:
            self.api_key = ''
            logger.error('Please set an API key!')
        self.reports = []

        if not session:
            session = requests.Session()
            adapter = requests.adapters.HTTPAdapter(pool_maxsize=20)
            session.mount("https://", adapter)
        self.session = session
        self.pool = ThreadPool(20)

    def add_report(self, report):
        if isinstance(report, list):
            for data in report:
                self.reports.append(data)
        else:
            self.reports.append(report)

    def send_report(self):
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'ApiKey ' + self.api_key
        }

        path = constants.COMPOSITE_DATA_PATH if config.rest_composite_data_enabled() else constants.PATH

        request_url = constants.HOST + path
        base_url = config.report_base_url()
        if base_url is not None:
            request_url = base_url + path

        if config.report_cw_enabled():
            if config.cw_composite_data_enabled():
                reports_json = self.prepare_composite_report_json()
                for report in reports_json:
                    print(report)
            else:
                for report in self.reports:
                    try:
                        print(json.dumps(report))
                    except TypeError:
                        logger.error(("Couldn't dump report with type {} to json string, "
                                    "probably it contains a byte array").format(report.get('type')))

            return []

        if config.rest_composite_data_enabled():
            reports_json = self.prepare_composite_report_json()
        else:
            reports_json = self.prepare_report_json()

        responses = []
        if len(reports_json) > 0:
            responses = self.pool.map(self.send_batch, [(request_url, headers, data) for data in reports_json])

        self.clear()
        return responses

    def send_batch(self, args):
        url, headers, data = args
        return self.session.post(url, data=data, headers=headers)

    def get_report_batches(self):
        batch_size = config.rest_composite_batchsize()
        if config.report_cw_enabled():
            batch_size = config.cloudwatch_composite_batchsize()

        batches = [self.reports[i:i + batch_size] for i in range(0, len(self.reports), batch_size)]
        return batches

    def prepare_report_json(self):
        batches = self.get_report_batches()
        batched_reports = []
        for batch in batches:
            report_jsons = []
            for report in batch:
                try:
                    report_jsons.append(json.dumps(report))
                except TypeError:
                    logger.error(("Couldn't dump report with type {} to json string, "
                                  "probably it contains a byte array").format(report.get('type')))
            json_string = "[{}]".format(','.join(report_jsons))
            batched_reports.append(json_string)
        return batched_reports

    def prepare_composite_report_json(self):
        invocation_report = None
        for report in self.reports:
            if report["type"] == "Invocation":
                invocation_report = report

        if not invocation_report:
            return []

        composite.init_composite_data_common_fields(invocation_report["data"])

        batches = self.get_report_batches()
        batched_reports = []

        for batch in batches:
            all_monitoring_data = [composite.remove_common_fields(report["data"]) for report in batch]
            composite_data = composite.get_composite_data(all_monitoring_data, self.api_key)
            try:
                batched_reports.append(json.dumps(composite_data))

            except TypeError:
                logger.error("Couldn't dump report with type Composite to json string, "
                             "probably it contains a byte array")

        composite.clear()
        return batched_reports

    def clear(self):
        self.reports.clear()
