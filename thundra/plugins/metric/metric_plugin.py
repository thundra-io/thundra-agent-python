import uuid
import threading
import gc
import time
import sys


from thundra import utils, constants
from thundra.opentracing.tracer import ThundraTracer


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
        self.reporter = {}
        self.tracer = ThundraTracer()

    def before_invocation(self, data):
        self.reporter = data['reporter']
        context = data['context']
        metric_time = time.time() * 1000
        function_name = getattr(context, constants.CONTEXT_FUNCTION_NAME, None)

        active_span = self.tracer.get_active_span()

        self.metric_data = {

            'type': "Metric",
            'agentVersion': '',
            'dataModelVersion': constants.DATA_FORMAT_VERSION,
            'applicationId': utils.get_application_id(context),
            'applicationDomainName':active_span.domain_name if active_span is not None else '',
            'applicationClassName': active_span.class_name if active_span is not None else '',
            'applicationName': function_name,
            'applicationVersion': getattr(context, constants.CONTEXT_FUNCTION_VERSION, None),
            'applicationStage': '',
            'applicationRuntime': 'python',
            'applicationRuntimeVersion': str(sys.version_info[0]),
            'applicationTags': {},

            'traceId': active_span.trace_id if active_span is not None else '',
            'transactionId': data['transactionId'],
            'spanId': active_span.span_id if active_span is not None else '',
            'metricTimestamp': int(metric_time),
            'tags':{}
        }
        self.system_cpu_total_start, self.system_cpu_usage_start = utils.system_cpu_usage()
        self.process_cpu_usage_start = utils.process_cpu_usage()

    def after_invocation(self, data):
        if 'contextId' in data:
            self.metric_data['rootExecutionAuditContextId'] = data['contextId']
        self.add_thread_metric_report()
        self.add_gc_metric_report()
        self.add_memory_metric_report()
        self.add_cpu_metric_report()

    def add_thread_metric_report(self):
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
            'apiKey': self.reporter.api_key,
            'dataModelVersion': constants.DATA_FORMAT_VERSION
        }
        self.reporter.add_report(thread_metric_report)

    def add_gc_metric_report(self):
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
            'apiKey': self.reporter.api_key,
            'dataModelVersion': constants.DATA_FORMAT_VERSION
        }
        self.reporter.add_report(gc_metric_report)

    def add_memory_metric_report(self):
        size, resident = utils.process_memory_usage()
        total_mem, free_mem = utils.system_memory_usage()
        used_mem = total_mem - free_mem
        memory_metric_data = {
            'id': str(uuid.uuid4()),
            'metricName': 'MemoryMetric',
        }
        metrics = {
            'app.maxMemory': int(size) if size is not None else -1,
            'app.usedMemory': int(resident) if resident is not None else -1,
            'sys.maxMemory': int(total_mem) if total_mem is not None else -1,
            'sys.usedMemory': int(used_mem) if used_mem is not None else -1
        }
        memory_metric_data.update(self.metric_data)
        memory_metric_data['metrics'] = metrics
        memory_metric_report = {
            'data': memory_metric_data,
            'type': 'Metric',
            'apiKey': self.reporter.api_key,
            'dataModelVersion': constants.DATA_FORMAT_VERSION
        }
        self.reporter.add_report(memory_metric_report)

    def add_cpu_metric_report(self):
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
            'apiKey': self.reporter.api_key,
            'dataModelVersion': constants.DATA_FORMAT_VERSION
        }
        self.reporter.add_report(cpu_metric_report)