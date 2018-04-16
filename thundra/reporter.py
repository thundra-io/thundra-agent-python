import json
import os

try:
    import requests
except ImportError:
    from botocore.vendored import requests

from thundra import constants
from thundra.utils import is_thundra_lambda_publish_cloudwatch_enabled


class Reporter:
    def __init__(self, api_key):
        if api_key is not None:
            self.api_key = api_key
        else:
            raise Exception('Please set an api key')
        self.reports = []

    def add_report(self, report):
        if is_thundra_lambda_publish_cloudwatch_enabled() == 'true':
            print(json.dumps(report))
        else:
            self.reports.append(report)

    def send_report(self):
        request_url = constants.HOST + constants.PATH
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'ApiKey ' + self.api_key
        }
        response = requests.post(request_url, headers=headers, data=json.dumps(self.reports))
        return response
