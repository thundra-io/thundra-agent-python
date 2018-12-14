import uuid
import threading
import gc
import time
import sys

from thundra import utils, constants
from thundra.opentracing.tracer import ThundraTracer
import thundra.application_support as application_support


class MetricPlugin:

    def __init__(self):
        self.hooks = {
            'before:invocation': self.before_invocation,
            'after:invocation': self.after_invocation
        }
        self.system_cpu_usage_start = float(0)
        self.system_cpu_usage_end = float(0)
        self.system_cpu_total_start = float(0)
        self.system_cpu_total_end = float(0)
        self.process_cpu_usage_start = float(0)
        self.process_cpu_usage_end = float(0)
        self.metric_data = {}
        self.tracer = ThundraTracer.get_instance()

    def before_invocation(self, plugin_context):
        context = plugin_context['context']
        function_name = getattr(context, constants.CONTEXT_FUNCTION_NAME, None)
        metric_time = time.time() * 1000

        active_span = self.tracer.get_active_span()

        self.metric_data = {
            'type': "Metric",
            'agentVersion': constants.THUNDRA_AGENT_VERSION,
            'dataModelVersion': constants.DATA_FORMAT_VERSION,
            'applicationId': utils.get_application_id(context),
            'applicationDomainName': constants.AWS_LAMBDA_APPLICATION_DOMAIN_NAME,
            'applicationClassName': constants.AWS_LAMBDA_APPLICATION_CLASS_NAME,
            'applicationName': function_name,
            'applicationVersion': getattr(context, constants.CONTEXT_FUNCTION_VERSION, None),
            'applicationStage': utils.get_configuration(constants.THUNDRA_APPLICATION_STAGE, ''),
            'applicationRuntime': 'python',
            'applicationRuntimeVersion': str(sys.version_info[0]),
            'applicationTags': {},

            'traceId': active_span.trace_id if active_span is not None else '',
            'transactionId': plugin_context.get('transaction_id', context.aws_request_id),
            'spanId': active_span.span_id if active_span is not None else '',
            'metricTimestamp': int(metric_time),
            'tags': {
                'aws.region': utils.get_configuration(constants.AWS_REGION, default='')
            }
        }
        self.system_cpu_total_start, self.system_cpu_usage_start = utils.system_cpu_usage()
        self.process_cpu_usage_start = utils.process_cpu_usage()

    def after_invocation(self, plugin_context):
        self.metric_data['applicationTags'] = application_support.get_application_tags()
        reporter = plugin_context['reporter']
        self.add_thread_metric_report(reporter)
        self.add_gc_metric_report(reporter)
        self.add_memory_metric_report(reporter)
        self.add_cpu_metric_report(reporter)

    def add_thread_metric_report(self, reporter):
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
            'apiKey': reporter.api_key,
            'dataModelVersion': constants.DATA_FORMAT_VERSION
        }
        reporter.add_report(thread_metric_report)

    def add_gc_metric_report(self, reporter):
        gc_metrics = gc.get_stats()
        gc_metric_data = {
            'id': str(uuid.uuid4()),
            'metricName': 'GCMetric'
        }
        gen = 0
        metrics = {}
        for metric in gc_metrics:
            key = 'generation' + str(gen) + 'Collections'
            metrics[key] = metric['collections']
            gen += 1
        gc_metric_data.update(self.metric_data)
        gc_metric_data['metrics'] = metrics
        gc_metric_report = {
            'data': gc_metric_data,
            'type': 'Metric',
            'apiKey': reporter.api_key,
            'dataModelVersion': constants.DATA_FORMAT_VERSION
        }
        reporter.add_report(gc_metric_report)

    def add_memory_metric_report(self, reporter):
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
            'apiKey': reporter.api_key,
            'dataModelVersion': constants.DATA_FORMAT_VERSION
        }
        reporter.add_report(memory_metric_report)

    def add_cpu_metric_report(self, reporter):
        self.process_cpu_usage_end = utils.process_cpu_usage()
        self.system_cpu_total_end, self.system_cpu_usage_end = utils.system_cpu_usage()
        process_cpu_load = 0
        system_cpu_load = 0
        system_cpu_total = self.system_cpu_total_end - self.system_cpu_total_start
        system_cpu_usage = self.system_cpu_usage_end - self.system_cpu_usage_start
        process_cpu_usage = self.process_cpu_usage_end - self.process_cpu_usage_start
        if system_cpu_total != 0:
            cpu_load = process_cpu_usage/system_cpu_total
            process_cpu_load = 1 if cpu_load > 1 else cpu_load
            cpu_load = system_cpu_usage/system_cpu_total
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
            'apiKey': reporter.api_key,
            'dataModelVersion': constants.DATA_FORMAT_VERSION
        }
        reporter.add_report(cpu_metric_report)
