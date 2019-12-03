from thundra.config.combined_property_accessor import CombinedPropertyAccessor
from thundra.config.system_environment_aware_property_accessor import SystemEnvironmentAwarePropertyAccessor


class StandardPropertyAccessor(CombinedPropertyAccessor):
    
    def __init__(self):
        super(StandardPropertyAccessor, self).__init__(property_accessors=self.createPropertyAccessors())
    
    @staticmethod
    def createPropertyAccessors():
        property_accessors = []
        property_accessors.append(SystemEnvironmentAwarePropertyAccessor())
        return property_accessors

    def put_property(self, property_name, property_value):
        self.props[property_name] = property_value

    def put_properties(self, properties):
        self.props.update(properties)

    def remove_property(self, property_name):
        del self.props[property_name]