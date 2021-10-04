import time
import uuid

def current_milli_time():
    return int(time.time() * 1000)


def create_uuid4():
    return str(uuid.uuid4())