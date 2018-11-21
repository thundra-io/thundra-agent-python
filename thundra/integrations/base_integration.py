"""
Base Event class
"""

from __future__ import absolute_import
import time
from .common import ErrorCode


class BaseIntegration(object):
    """
    Serves as a base class for all integrations
    """

    CLASS_TYPE = 'base'

    def __init__(self):
        self.event_id = ''
        self.error_code = ErrorCode.OK
        self.exception = {}

        self.resource = {
            'type': self.CLASS_TYPE,
            'name': '',
            'operation': '',
            'metadata': {},
        }

    def set_error(self):
        """
        Sets general error.
        :return: None
        """

        self.error_code = ErrorCode.ERROR

    def set_exception(self, exception, traceback_data, scope):
        """
        Sets exception data on event.
        :param exception: Exception object
        :param traceback_data: traceback string
        :return: None
        """

        self.error_code = ErrorCode.EXCEPTION
        self.exception['type'] = type(exception).__name__
        self.exception['message'] = str(exception)
        self.exception['traceback'] = traceback_data
        self.exception['time'] = time.time()
