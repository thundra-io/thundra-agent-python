import logging

logs = []


class ThundraLogHandler(logging.Handler):
    def __init__(self):
        logging.Handler.__init__(self)
        ThundraLogHandler.logs = []

    def emit(self, record):
        formatted_message = self.format(record)
        log = {
            'log': formatted_message,
            'logMessage': record.msg,
            'loggerName': record.name,
            'logTimestamp': int(record.created * 1000),
            'logLevel': record.levelname,
            'logLevelId': record.levelno / 10
        }
        logs.append(log)


logging.ThundraLogHandler = ThundraLogHandler
