from thundra.plugins.config.base_plugin_config import BasePluginConfig


class TraceConfig(BasePluginConfig):
    def __init__(self, opts=None):
        if opts is None:
            opts = {}
        super(TraceConfig, self).__init__(enabled=opts.get('enabled', True))
        self.sampler = opts.get('sampler')
