import time
import uuid

def current_milli_time():
    return int(time.time() * 1000)


def create_uuid4():
    return str(uuid.uuid4())


def print_debug_message_to_console(msg):
    from thundra.plugins.log.thundra_logger import debug_logger
    from thundra.config.config_provider import ConfigProvider
    from thundra.config import config_names
    if ConfigProvider.get(config_names.THUNDRA_DEBUG_ENABLE):
        debug_logger("[THUNDRA] " + msg)