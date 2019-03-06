from thundra import config, constants
from thundra.plugins.invocation import invocation_support
from thundra.integrations.base_integration import BaseIntegration


class ElasticsearchIntegration(BaseIntegration):
    CLASS_TYPE = 'elasticsearch'

    def __init__(self):
        pass

    def get_operation_name(self, wrapped, instance, args, kwargs):
        pass

    def before_call(self, scope, wrapped, instance, args, kwargs, response, exception):
        print("before es call")
    
    def after_call(self, scope, wrapped, instance, args, kwargs, response, exception):
        print("after es call")
