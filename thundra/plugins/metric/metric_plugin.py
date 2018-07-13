import uuid
import threading
import gc
import time



from thundra import utils, constants


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
        self.stat_data = {}
        self.reporter = {}

    def before_invocation(self, data):
        self.reporter = data['reporter']
        context = data['context']
        stat_time = time.time() * 1000
        self.stat_data = {
            'transactionId': data['transactionId'],
            'applicationName': getattr(context, 'function_name', None),
            'applicationId': utils.get_application_id(context),
            'applicationVersion': getattr(context, constants.CONTEXT_FUNCTION_VERSION, None),
            'applicationProfile': utils.get_environment_variable(constants.THUNDRA_APPLICATION_PROFILE, ''),
            'applicationType': 'python',
            'functionRegion': utils.get_environment_variable(constants.AWS_REGION, ''),
            'statTimestamp': int(stat_time)
        }
        self.system_cpu_total_start, self.system_cpu_usage_start = utils.system_cpu_usage()
        self.process_cpu_usage_start = utils.process_cpu_usage()

    def after_invocation(self, data):
        if 'contextId' in data:
            self.stat_data['rootExecutionAuditContextId'] = data['contextId']
        self.add_thread_stat_report()
        self.add_gc_stat_report()
        self.add_memory_stat_report()
        self.add_cpu_stat_report()

    def add_thread_stat_report(self):
        active_thread_counts = threading.active_count()
        thread_stat_data = {
            'id': str(uuid.uuid4()),
            'statName': 'ThreadStat',
            'threadCount': active_thread_counts
        }
        thread_stat_data.update(self.stat_data)
        thread_stat_report = {
            'data': thread_stat_data,
            'type': 'StatData',
            'apiKey': self.reporter.api_key,
            'dataFormatVersion': constants.DATA_FORMAT_VERSION
        }
        self.reporter.add_report(thread_stat_report)

    def add_gc_stat_report(self):
        gc_stats = gc.get_stats()
        gc_stat_data = {
            'id': str(uuid.uuid4()),
            'statName': 'GCStat'
        }
        gen = 0
        for stat in gc_stats:
            key = 'generation' + str(gen) + 'Collections'
            gc_stat_data[key] = stat['collections']
            gen += 1
        gc_stat_data.update(self.stat_data)
        gc_stat_report = {
            'data': gc_stat_data,
            'type': 'StatData',
            'apiKey': self.reporter.api_key,
            'dataFormatVersion': constants.DATA_FORMAT_VERSION
        }
        self.reporter.add_report(gc_stat_report)

    def add_memory_stat_report(self):
        size, resident = utils.process_memory_usage()
        total_mem, free_mem = utils.system_memory_usage()
        used_mem = total_mem - free_mem
        memory_stat_data = {
            'id': str(uuid.uuid4()),
            'statName': 'MemoryStat',
            'size': size,
            'resident': resident,
            'totalMemory': total_mem,
            'usedMemory': used_mem
        }
        memory_stat_data.update(self.stat_data)
        memory_stat_report = {
            'data': memory_stat_data,
            'type': 'StatData',
            'apiKey': self.reporter.api_key,
            'dataFormatVersion': constants.DATA_FORMAT_VERSION
        }
        self.reporter.add_report(memory_stat_report)

    def add_cpu_stat_report(self):
        self.system_cpu_total_end, self.system_cpu_usage_end = utils.system_cpu_usage()
        self.process_cpu_usage_end = utils.process_cpu_usage()
        process_cpu_load = 0
        system_cpu_load = 0
        system_cpu_total = self.system_cpu_total_end - self.system_cpu_total_start
        system_cpu_usage = self.system_cpu_usage_end - self.system_cpu_usage_start
        process_cpu_usage = self.process_cpu_usage_end - self.process_cpu_usage_start
        if system_cpu_total != 0:
            process_cpu_load = process_cpu_usage/system_cpu_total
            system_cpu_load = system_cpu_usage/system_cpu_total

        cpu_stat_data = {
            'id': str(uuid.uuid4()),
            'statName': 'CPUStat',
            'processCpuLoad': process_cpu_load,
            'systemCpuLoad': system_cpu_load
        }
        cpu_stat_data.update(self.stat_data)
        cpu_stat_report = {
            'data': cpu_stat_data,
            'type': 'StatData',
            'apiKey': self.reporter.api_key,
            'dataFormatVersion': constants.DATA_FORMAT_VERSION
        }
        self.reporter.add_report(cpu_stat_report)