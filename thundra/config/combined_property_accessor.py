from thundra.config.property_accessor import PropertyAccessor


class CombinedPropertyAccessor(PropertyAccessor):

    def __init__(self, props = {}, property_accessors=[]):
        self.props = props
        self.property_accessors = property_accessors

        for property_accessor in self.property_accessors:
            self.props.update(property_accessor.get_properties())

    def get_property(self, property_name, default=None):
        return self.props.get(property_name, default)

    def get_properties(self):
        return self.props.copy()