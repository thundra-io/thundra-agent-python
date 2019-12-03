import os

from thundra.config import utils

lambda_context = None

def set_current_context(context):
    global lambda_context
    lambda_context = context


def get_current_context():
    return lambda_context


def initialize_properties():
    property_accessor = utils.get_property_accessor()
    initialize_properties_from_environment_variables(property_accessor)


def initialize_properties_from_environment_variables(property_accessor):
    env_variables = os.environ

    for var_name in env_variables:
        val = env_variables.get(var_name).strip()
        if var_name.startswith("x_thundra_"):
            var_name = var_name[2:]

        if var_name.startswith("thundra_agent_lambda"):
            var_name = var_name.replace("thundra_agent_lambda", "thundra_agent", 1)

        if var_name.startswith("thundra_"):
            property_accessor.put_property(var_name, val)

    