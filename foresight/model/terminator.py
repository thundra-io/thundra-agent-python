from thundra.utils import Singleton
import foresight.utils.generic_utils as utils
import logging, threading

logger = logging.getLogger(__name__)

class ThreadExecutorTerminator(threading.Thread):
    def __init__(self, *args, **kwargs):
        threading.Thread.__init__(self)
        self.event = threading.Event()
        
    def run(self):
        terminator = Terminator()
        terminator.wait()

class Terminator(Singleton):
    def __init__(self):
        self.tasks = []

    def register_task(self, task): # task => BaseWrapper 
        self.tasks.append(task)

    def wait(self):
        for task in self.tasks:
            try:
                task.thread_pool_executor.shutdown(wait=True)
            except Exception as e:
                logger.error(f"Task wait error in Terminator".format(e))