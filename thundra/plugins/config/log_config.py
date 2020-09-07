from thundra.plugins.config.base_plugin_config import BasePluginConfig


class LogConfig(BasePluginConfig):
    def __init__(self, enabled=False, sampler=None):
        super(LogConfig, self).__init__(enabled=enabled)
        self.sampler = sampler
