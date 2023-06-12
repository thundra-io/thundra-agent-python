import abc
import logging
import time
from concurrent import futures

from catchpoint.compat import PY2, queue
from catchpoint.config import config_names
from catchpoint.config.config_provider import ConfigProvider
from catchpoint.plugins.config.catchpoint_config import CatchpointConfig
from catchpoint.reporter import Reporter

ABC = abc.ABCMeta('ABC', (object,), {})

logger = logging.getLogger(__name__)


class ThreadPoolExecutorWithQueueSizeLimit(futures.ThreadPoolExecutor):
    def __init__(self, maxsize=10000, *args, **kwargs):
        super(ThreadPoolExecutorWithQueueSizeLimit, self).__init__(*args, **kwargs)
        self._work_queue = NoWaitQueue(maxsize=maxsize)


class NoWaitQueue(queue.Queue):
    def __init__(self, *args, **kwargs):
        queue.Queue.__init__(self, *args, **kwargs)

    def put(self, item, **kwargs):
        queue.Queue.put(self, item, block=False)


class BaseWrapper(ABC):

    def __init__(self, api_key=None, disable_trace=False, disable_metric=True, disable_log=True, opts=None):
        self.plugins = None
        self.config = CatchpointConfig()
        if opts is not None:
            self.config = CatchpointConfig(opts)

        self.api_key = ConfigProvider.get(config_names.CATCHPOINT_APIKEY, api_key)
        if not self.api_key:
            self.api_key = self.config.api_key
        if self.api_key is None:
            logger.error('Please set "catchpoint_apiKey" from environment variables in order to use Catchpoint')

        self.reporter = Reporter(self.api_key)
        self.debugger_process = None

        if not ConfigProvider.get(config_names.CATCHPOINT_TRACE_INSTRUMENT_DISABLE):
            if not PY2:
                from catchpoint.plugins.trace.patcher import ImportPatcher
                self.import_patcher = ImportPatcher()
        self.thread_pool_executor = ThreadPoolExecutorWithQueueSizeLimit()


    def execute_hook(self, name, data):
        if name == 'after:invocation':
            [plugin.hooks[name](data) for plugin in reversed(self.plugins) if hasattr(plugin, 'hooks')
             and name in plugin.hooks]
        else:
            [plugin.hooks[name](data) for plugin in self.plugins if
             hasattr(plugin, 'hooks') and name in plugin.hooks]


    def prepare_and_send_reports(self, execution_context):
        execution_context.finish_timestamp = int(time.time() * 1000)
        self.execute_hook('after:invocation', execution_context)
        self.reporter.send_reports(execution_context.reports)


    def prepare_and_send_reports_async(self, execution_context):
        execution_context.finish_timestamp = int(time.time() * 1000)
        self.execute_hook('after:invocation', execution_context)
        try:
            self.thread_pool_executor.submit(self.reporter.send_reports, execution_context.reports)
        except queue.Full:
            logger.error("Dropping the monitoring report as the request queue is full")
        except Exception as e:
            logger.error(e)