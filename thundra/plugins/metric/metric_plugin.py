import gc
import logging
import threading
import time
import uuid

from thundra import utils, constants
from thundra.compat import PY2
from thundra.opentracing.tracer import ThundraTracer
from thundra.plugins.config.metric_config import MetricConfig
from thundra.plugins.metric import metric_support

logger = logging.getLogger(__name__)


class MetricPlugin:

    def __init__(self, plugin_context=None, config=None):
        self.metric_data = {}
        self.plugin_context = plugin_context
        self.tracer = ThundraTracer.get_instance()
        self.system_cpu_usage_start = float(0)
        self.system_cpu_usage_end = float(0)
        self.system_cpu_total_start = float(0)
        self.system_cpu_total_end = float(0)
        self.process_cpu_usage_start = float(0)
        self.process_cpu_usage_end = float(0)
        self.hooks = {
            'before:invocation': self.before_invocation,
            'after:invocation': self.after_invocation
        }

        if isinstance(config, MetricConfig):
            self.config = config
        else:
            self.config = MetricConfig()

    def before_invocation(self, execution_context):
        metric_time = time.time() * 1000
        active_span = self.tracer.get_active_span()

        self.metric_data = {
            'type': "Metric",
            'agentVersion': constants.THUNDRA_AGENT_VERSION,
            'dataModelVersion': constants.DATA_FORMAT_VERSION,
            'traceId': active_span.trace_id if active_span is not None else '',
            'transactionId': execution_context.transaction_id,
            'spanId': active_span.span_id if active_span is not None else '',
            'metricTimestamp': int(metric_time),
            'tags': {
                'aws.region': utils.get_env_variable(constants.AWS_REGION, default='')
            }
        }
        # Add application related data
        application_info = self.plugin_context.application_info
        self.metric_data.update(application_info)
        self.system_cpu_total_start, self.system_cpu_usage_start = utils.system_cpu_usage()
        self.process_cpu_usage_start = utils.process_cpu_usage()

    def after_invocation(self, execution_context):
        if not self.check_sampled():
            return

        self.add_thread_metric_report(execution_context)
        self.add_gc_metric_report(execution_context)
        self.add_memory_metric_report(execution_context)
        self.add_cpu_metric_report(execution_context)

    def check_sampled(self):
        sampler = metric_support.get_sampler()
        if self.config.sampler:
            sampler = self.config.sampler
        sampled = True
        if sampler is not None:
            try:
                sampled = sampler.is_sampled(self.metric_data)
            except Exception as e:
                logger.error("error while sampling metrics: %s", e)
        return sampled

    def add_thread_metric_report(self, execution_context):
        active_thread_counts = threading.active_count()
        thread_metric_data = {
            'id': str(uuid.uuid4()),
            'metricName': 'ThreadMetric',
        }
        metrics = {
            'threadCount': active_thread_counts if active_thread_counts is not None else -1
        }
        thread_metric_data.update(self.metric_data)
        thread_metric_data['metrics'] = metrics
        thread_metric_report = {
            'data': thread_metric_data,
            'type': 'Metric',
            'apiKey': self.plugin_context.api_key,
            'dataModelVersion': constants.DATA_FORMAT_VERSION
        }
        execution_context.report(thread_metric_report)

    def add_gc_metric_report(self, execution_context):
        gc_metrics = gc.get_count()
        if not PY2:
            gc_metrics = gc.get_stats()

        gc_metric_data = {
            'id': str(uuid.uuid4()),
            'metricName': 'GCMetric'
        }

        gen = 0
        metrics = {}
        for metric in gc_metrics:
            key = 'generation' + str(gen) + 'Collections'
            if PY2:
                metrics[key] = metric
            else:
                metrics[key] = metric['collections']
            gen += 1
        gc_metric_data.update(self.metric_data)
        gc_metric_data['metrics'] = metrics
        gc_metric_report = {
            'data': gc_metric_data,
            'type': 'Metric',
            'apiKey': self.plugin_context.api_key,
            'dataModelVersion': constants.DATA_FORMAT_VERSION
        }
        execution_context.report(gc_metric_report)

    def add_memory_metric_report(self, execution_context):
        size, used = utils.process_memory_usage()
        memory_metric_data = {
            'id': str(uuid.uuid4()),
            'metricName': 'MemoryMetric',
        }
        metrics = {
            'app.maxMemory': size,
            'app.usedMemory': used
        }
        memory_metric_data.update(self.metric_data)
        memory_metric_data['metrics'] = metrics
        memory_metric_report = {
            'data': memory_metric_data,
            'type': 'Metric',
            'apiKey': self.plugin_context.api_key,
            'dataModelVersion': constants.DATA_FORMAT_VERSION
        }
        execution_context.report(memory_metric_report)

    def add_cpu_metric_report(self, execution_context):
        self.process_cpu_usage_end = utils.process_cpu_usage()
        self.system_cpu_total_end, self.system_cpu_usage_end = utils.system_cpu_usage()
        process_cpu_load = 0
        system_cpu_load = 0
        system_cpu_total = self.system_cpu_total_end - self.system_cpu_total_start
        system_cpu_usage = self.system_cpu_usage_end - self.system_cpu_usage_start
        process_cpu_usage = self.process_cpu_usage_end - self.process_cpu_usage_start
        if system_cpu_total != 0:
            cpu_load = process_cpu_usage / system_cpu_total
            process_cpu_load = 1 if cpu_load > 1 else cpu_load
            cpu_load = system_cpu_usage / system_cpu_total
            system_cpu_load = 1 if cpu_load > 1 else cpu_load

        cpu_metric_data = {
            'id': str(uuid.uuid4()),
            'metricName': 'CPUMetric'
        }

        metrics = {
            'app.cpuLoad': process_cpu_load if process_cpu_load is not None else -1,
            'sys.cpuLoad': system_cpu_load if system_cpu_load is not None else -1
        }
        cpu_metric_data.update(self.metric_data)
        cpu_metric_data['metrics'] = metrics
        cpu_metric_report = {
            'data': cpu_metric_data,
            'type': 'Metric',
            'apiKey': self.plugin_context.api_key,
            'dataModelVersion': constants.DATA_FORMAT_VERSION
        }
        execution_context.report(cpu_metric_report)
