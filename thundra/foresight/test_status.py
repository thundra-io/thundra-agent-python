from enum import Enum

class AutoNumber(Enum):
     def __new__(cls):
        value = len(cls.__members__)  # note no + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

class TestStatus(AutoNumber):
    SUCCESSFUL = ()
    FAILED = ()
    ABORTED = ()
    IGNORED = ()
 