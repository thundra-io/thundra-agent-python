import sys

_ver = sys.version_info

# Python 2.x
PY2 = (_ver[0] == 2)

# Python 3.x
PY3 = (_ver[0] == 3)

# Python 2.7.x
PY27 = (PY2 and _ver[1] == 7)

# Python 3.6.x
PY36 = (PY3 and _ver[1] == 6)

# Python 3.7.x
PY37 = (PY3 and _ver[1] == 7)

# Python 3.8.x
PY38 = (PY3 and _ver[1] == 8)

class TimeoutError(Exception):
    def __init__(self, msg="Task timed out"):
        super(TimeoutError, self).__init__(msg)

if PY2:
    from urlparse import urlparse

    builtin_str = str
    bytes = str
    str = unicode
    basestring = basestring


elif PY3:
    from urllib.parse import urlparse

    builtin_str = str
    str = str
    bytes = bytes
    basestring = (str, bytes)
    numeric_types = (int, float)
