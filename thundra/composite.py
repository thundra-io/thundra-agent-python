import uuid

from thundra import constants

_common_fields_list = [
    'agentVersion',
    'dataModelVersion',
    'applicationId',
    'applicationDomainName',
    'applicationClassName',
    'applicationName',
    'applicationVersion',
    'applicationStage',
    'applicationRuntime',
    'applicationRuntimeVersion',
    'applicationTags'
]


def init_composite_data_common_fields(data):
    return {field: data.get(field) for field in _common_fields_list}


def remove_common_fields(data):
    without_common_fields = data.copy()
    for field in _common_fields_list:
        try:
            del without_common_fields[field]
        except (KeyError, TypeError):
            pass
    return without_common_fields


def get_composite_data(all_monitoring_data, api_key, data):
    composite_data = {
        "type": "Composite", "dataModelVersion": constants.DATA_FORMAT_VERSION,
        "apiKey": api_key,
        'data': data
    }
    composite_data['data']['id'] = str(uuid.uuid4())
    composite_data['data']['type'] = "Composite"
    composite_data['data']['allMonitoringData'] = all_monitoring_data
    return composite_data
