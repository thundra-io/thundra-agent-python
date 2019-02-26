import logging
from thundra import config


loggers = {}

def get_logger(name):
    global loggers
    if loggers.get(name):
        return loggers.get(name)
    else:
        FORMAT = "%(asctime)s  - %(levelname)s - %(name)s - %(message)s"
        if name is None:
            logger = logging.getLogger(__name__)
        else:
            logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        ch_format = logging.Formatter(FORMAT)
        console_handler.setFormatter(ch_format)
        logger.addHandler(console_handler)
        loggers[name] = logger
        return logger


def log_to_console(message,  handler):
    logger = get_logger(handler)
    logging.getLogger().handlers = []
    logger.debug(message)


def debug_logger(msg, handler=None):
    if config.debug_enabled():
        if hasattr(msg, '__dict__'):
            log_to_console(msg, handler)
            display = vars(msg)
            log_to_console(display, handler)
            for key, value in display.items():
                debug_logger_helper(getattr(msg, key), handler)
        else:
            log_to_console(msg, handler)


def debug_logger_helper(msg, handler):
    if hasattr(msg, '__dict__'):
        log_to_console(msg, handler)
        display = vars(msg)
        log_to_console(display,  handler)
        for key, value in display.items():
            debug_logger_helper(getattr(msg, key), handler)
