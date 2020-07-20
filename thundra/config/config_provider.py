import os
 
from thundra.config.config_metadata import CONFIG_METADATA
from thundra.utils import str2bool

class ConfigProvider:
    configs = {}

    @staticmethod
    def __init__():
        ConfigProvider.initialize_config_from_environment_variables()
        ConfigProvider.add_non_lambda_aliases()

    @staticmethod
    def initialize_config_from_environment_variables():
        env_variables = os.environ

        for var_name in env_variables:
            if var_name.upper().startswith("THUNDRA_"):
                env_var_name = ConfigProvider.env_var_to_config_name(var_name)
                val = env_variables.get(var_name).strip()
                env_var_type = ConfigProvider.get_config_type(env_var_name)
                ConfigProvider.configs[env_var_name] = ConfigProvider.parse(val, env_var_type)

    @staticmethod
    def add_non_lambda_aliases():
        for config_name in ConfigProvider.configs:
            if config_name.startswith('thundra.agent.lambda'):
                value = ConfigProvider.configs[config_name]
                ConfigProvider.configs[config_name.replace('thundra.agent.lambda', 'thundra.agent', 1)] = value

    @staticmethod
    def get(key, default_value=None):
        value = ConfigProvider.configs.get(key)
        if value != None:
            return value
        if default_value != None:
            return default_value
        if CONFIG_METADATA.get(key):
            return CONFIG_METADATA[key].get('defaultValue')
        return None

    @staticmethod
    def get_config_type(config_name):
        config_metadata = CONFIG_METADATA.get(config_name)
        if config_metadata:
            return config_metadata.get('type')
        else:
            if config_name.startswith('thundra.agent.lambda.'):
                config_name = config_name.replace('thundra.agent.lambda.', 'thundra.agent.', 1)
                config_metadata = CONFIG_METADATA.get(config_name)
                return config_metadata.get('type')
        return 'string'

    @staticmethod
    def parse(value, var_type):
        if var_type == 'string':
            return value
        if var_type == 'int':
            return ConfigProvider.convert_to_int(value)
        if var_type == 'boolean':
            return ConfigProvider.convert_to_bool(value)
        return value

    @staticmethod
    def convert_to_bool(value, default=False):
        try:
            return str2bool(value)
        except ValueError:
            return default

    @staticmethod
    def convert_to_int(value, default=0):
        try:
            return int(value)
        except (ValueError, TypeError):
            return default

    @staticmethod
    def config_name_to_env_var(config_name):
        return config_name.upper().replace('.', '_')

    @staticmethod
    def env_var_to_config_name(env_var_name):
        return env_var_name.lower().replace('_', '.')

    @staticmethod
    def clear():
        ConfigProvider.configs.clear()
    
    @staticmethod
    def set(key, value):
        ConfigProvider.configs[key] = ConfigProvider.parse(value, ConfigProvider.get_config_type(key))