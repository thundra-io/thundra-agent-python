class PluginContext:

    def __init__(self, **opts):
        self.application_info = opts.get('application_info')
        self.request_count = opts.get('request_count', 0)
        self.api_key = opts.get('api_key')
        self.executor = opts.get('executor')
