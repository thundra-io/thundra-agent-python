import signal
import sys
import threading


class ThreadTimeout(object):
    def __init__(self, seconds, handler, execution_context):
        self.seconds = seconds
        self.timer = None
        self.handler = handler
        self.execution_context = execution_context

    def __enter__(self):
        self.timer = threading.Timer(self.seconds, self.handler, [self.execution_context])
        if self.seconds > 0:
            self.timer.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.timer:
            self.timer.cancel()
        return False


class SignalTimeout(object):
    def __init__(self, seconds, handler, execution_context):
        self.seconds = seconds
        self.handler = handler
        self.execution_context = execution_context

    def __enter__(self):
        if threading.current_thread().__class__.__name__ == '_MainThread':
            signal.signal(signal.SIGALRM, self._timeout)
            if self.seconds > 0:
                signal.setitimer(signal.ITIMER_REAL, self.seconds)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if threading.current_thread().__class__.__name__ == '_MainThread':
            signal.setitimer(signal.ITIMER_REAL, 0)
        return False

    def _timeout(self, signum, frame):
        current_thread = threading.current_thread().__class__.__name__
        if current_thread == '_MainThread' and signum == signal.SIGALRM:
            self.handler(self.execution_context)


if sys.platform == "win32":
    Timeout = ThreadTimeout
else:
    Timeout = SignalTimeout
