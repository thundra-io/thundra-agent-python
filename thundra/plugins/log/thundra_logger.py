import logging

from thundra.config import config_names
from thundra.config.config_provider import ConfigProvider

loggers = {}


class StreamToLogger(object):
    def __init__(self, logger, stdout):
        self.logger = logger
        self.stdout = stdout

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.info(line.rstrip())
        self.stdout.write(buf)

    def flush(self):
        self.stdout.flush()


def get_logger(name):
    global loggers
    if loggers.get(name):
        return loggers.get(name)
    else:
        format = "%(asctime)s  - %(levelname)s - %(name)s - %(message)s"
        if name is None:
            logger = logging.getLogger(__name__)
        else:
            logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        ch_format = logging.Formatter(format)
        console_handler.setFormatter(ch_format)
        logger.addHandler(console_handler)
        loggers[name] = logger
        return logger


def log_to_console(message, handler):
    logger = get_logger(handler)
    logging.getLogger().handlers = []
    logger.debug(message)


def debug_logger(msg, handler=None):
    if ConfigProvider.get(config_names.THUNDRA_DEBUG_ENABLE):
        if hasattr(msg, '__dict__'):
            log_to_console(msg, handler)
            display = vars(msg)
            log_to_console(display, handler)
            for key, _ in display.items():
                debug_logger_helper(getattr(msg, key), handler)
        else:
            log_to_console(msg, handler)


def debug_logger_helper(msg, handler):
    if hasattr(msg, '__dict__'):
        log_to_console(msg, handler)
        display = vars(msg)
        log_to_console(display, handler)
        for key, _ in display.items():
            debug_logger_helper(getattr(msg, key), handler)
