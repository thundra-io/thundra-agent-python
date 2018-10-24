import logging
from thundra import constants
import thundra.utils as utils


def get_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    return logger


def log_to_console(message):
    logger = get_logger()
    logger.debug(message)


def debug_logger(msg):
    if utils.get_configuration(constants.THUNDRA_LAMBDA_DEBUG_ENABLE, 'false') == 'true':
        if hasattr(msg, '__dict__'):
            log_to_console(msg)
            display = vars(msg)
            log_to_console(display)
            for key, value in display.items():
                debug_logger_helper(getattr(msg, key))
        else:
            log_to_console(msg)


def debug_logger_helper(msg):
    if hasattr(msg, '__dict__'):
        log_to_console(msg)
        display = vars(msg)
        log_to_console(display)
        for key, value in display.items():
            debug_logger_helper(getattr(msg, key))
