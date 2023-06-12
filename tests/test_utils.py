import os
from catchpoint import utils, constants


def test_get_default_timeout_margin(monkeypatch):
    monkeypatch.setitem(os.environ, constants.AWS_REGION, 'us-west-2')
    timeout_margin = utils.get_default_timeout_margin()
    assert timeout_margin == 200

    monkeypatch.setitem(os.environ, constants.AWS_REGION, 'us-east-2')

    timeout_margin = utils.get_default_timeout_margin()
    assert timeout_margin == 600

    monkeypatch.setitem(os.environ, constants.AWS_REGION, 'eu-west-1')

    timeout_margin = utils.get_default_timeout_margin()
    assert timeout_margin == 1000

    monkeypatch.setitem(os.environ, constants.AWS_REGION, 'eu-west-1')
    monkeypatch.setitem(os.environ, constants.AWS_LAMBDA_FUNCTION_MEMORY_SIZE, '1536')

    timeout_margin = utils.get_default_timeout_margin()
    assert timeout_margin == 1000

    monkeypatch.setitem(os.environ, constants.AWS_REGION, 'eu-west-1')
    monkeypatch.setitem(os.environ, constants.AWS_LAMBDA_FUNCTION_MEMORY_SIZE, '128')

    timeout_margin = utils.get_default_timeout_margin()
    assert timeout_margin == 3000


def test_get_nearest_collector(monkeypatch):
    regions = [ 'us-west-2', 'us-west-1', 'us-east-2', 'us-east-1', 'ca-central-1', 'sa-east-1',
            'eu-central-1', 'eu-west-1', 'eu-west-2', 'eu-west-3', 'eu-north-1', 'eu-south-1',
            'ap-south-1', 'ap-northeast-1', 'ap-northeast-2', 'ap-southeast-1', 'ap-southeast-2', 
            'ap-east-1', 'af-south-1', 'me-south-1']

    for region in regions:
        monkeypatch.setitem(os.environ, constants.AWS_REGION, region)
        collector = utils.get_nearest_collector()
        assert collector == "{}.collector.catchpoint.com".format(region)
    
    monkeypatch.delitem(os.environ, constants.AWS_REGION)
    collector = utils.get_nearest_collector()
    assert collector == "collector.catchpoint.com"
