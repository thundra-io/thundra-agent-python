import json

try:
    import requests
except ImportError:
    from botocore.vendored import requests

from thundra import constants
from thundra.utils import get_environment_variable
import thundra.utils as utils

class Reporter:
    def __init__(self, api_key):
        if api_key is not None:
            self.api_key = api_key
        else:
            raise Exception('Please set an api key')
        self.reports = []

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
        try:
            base_url = utils.get_environment_variable(constants.THUNDRA_LAMBDA_PUBLISH_REST_BAESURL)
            if base_url is not None:
                request_url = base_url + '/monitor-datas'
        except KeyError:
            pass

        response = requests.post(request_url, headers=headers, data=json.dumps(self.reports))
        return response
