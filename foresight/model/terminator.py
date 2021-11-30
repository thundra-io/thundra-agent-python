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
        terminator._wait()

class Terminator(Singleton):
    def __init__(self):
        self.tasks = []


    def register_task(self, task): # task => BaseWrapper 
        self.tasks.append(task)


    def _wait(self):
        for task in self.tasks:
            try:
                task.thread_pool_executor.shutdown(wait=True)
            except Exception as e:
                logger.error(f"Task wait error in Terminator".format(e))


    def wait(self, timeout=30):
        terminator_thread = ThreadExecutorTerminator()
        terminator_thread.start()
        terminator_thread.join(timeout)
        if terminator_thread.is_alive():
            logger.debug("Thread is killed by event!")
            terminator_thread.event.set()
        else:
            logger.debug("Thread has already finished!")