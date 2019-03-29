import json
import logging

from thundra import constants, config
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
        if config.report_cw_enabled():
            try:
                print(json.dumps(report))
            except TypeError:
                logger.error("Couldn't dump report with type {} to json string, \
                    probably it contains a byte array".format(report.get('type')))
        else:
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
        request_url = constants.HOST + constants.PATH
        base_url = config.report_base_url()
        if base_url is not None:
            request_url = base_url + '/monitoring-data'

        batches = self.get_report_batches()
        reports_json = [self.prepare_report_json(batch) for batch in batches]

        responses = []
        if len(batches) > 1:
            responses = self.pool.map(self.send_batch, [(request_url, headers, data) for data in reports_json])

        else:
            response = self.session.post(request_url, headers=headers, data=self.prepare_report_json(self.reports))
            responses.append(response)

        self.clear()
        return responses

    def send_batch(self, args):
        url, headers, data = args
        return self.session.post(url, data=data, headers=headers)

    def get_report_batches(self):
        batch_size = constants.MAX_MONITOR_DATA_BATCH_SIZE
        batches = [self.reports[i:i + batch_size] for i in range(0, len(self.reports), batch_size)]
        return batches

    def prepare_report_json(self, batch):
        report_jsons = []
        for report in batch:
            try:
                report_jsons.append(json.dumps(report))
            except TypeError:
                logger.error(("Couldn't dump report with type {} to json string, "
                              "probably it contains a byte array").format(report.get('type')))
        json_string = "[{}]".format(','.join(report_jsons))
        return json_string

    def clear(self):
        self.reports.clear()
