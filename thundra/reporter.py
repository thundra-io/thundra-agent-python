import json
import logging

try:
    import requests
except ImportError:
    from botocore.vendored import requests

from thundra import constants
from thundra.utils import get_environment_variable
import thundra.utils as utils

logger = logging.getLogger(__name__)

class Reporter:
    def __init__(self, api_key, session=None):
        if api_key is not None:
            self.api_key = api_key
        else:
            self.api_key = ''
            logger.error('Please set an API key!')
        self.reports = []

        if not session:
            session = requests.Session()
        self.session=session

    def add_report(self, report):
        if get_environment_variable(constants.THUNDRA_LAMBDA_PUBLISH_CLOUDWATCH_ENABLE) == 'true':
            print(json.dumps(report))
        else:
            self.reports.append(report)

    def send_report(self):
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'ApiKey ' + self.api_key
        }
        request_url = constants.HOST + constants.PATH
        base_url = utils.get_environment_variable(constants.THUNDRA_LAMBDA_PUBLISH_REST_BASEURL)
        if base_url is not None:
            request_url = base_url + '/monitor-datas'

        response = self.session.post(request_url, headers=headers, data=json.dumps(self.reports))
        self.reports.clear()
        return response
