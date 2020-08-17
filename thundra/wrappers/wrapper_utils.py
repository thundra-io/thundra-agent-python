from thundra import ConfigProvider
from thundra.config import config_names
from thundra.plugins.invocation.invocation_plugin import InvocationPlugin
from thundra.plugins.log.log_plugin import LogPlugin
from thundra.plugins.metric.metric_plugin import MetricPlugin
from thundra.plugins.trace.trace_plugin import TracePlugin


def initialize_plugins(plugin_context, disable_trace, disable_metric, disable_log):
    plugins = []
    if not ConfigProvider.get(config_names.THUNDRA_TRACE_DISABLE, disable_trace):
        plugins.append(TracePlugin(plugin_context=plugin_context))
    plugins.append(InvocationPlugin(plugin_context=plugin_context))

    if not ConfigProvider.get(config_names.THUNDRA_METRIC_DISABLE, disable_metric):
        plugins.append(MetricPlugin(plugin_context=plugin_context))

    if not ConfigProvider.get(config_names.THUNDRA_LOG_DISABLE, disable_log):
        plugins.append(LogPlugin(plugin_context=plugin_context))
    return plugins
