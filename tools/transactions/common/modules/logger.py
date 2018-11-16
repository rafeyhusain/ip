import json
import logging
from logging.handlers import SysLogHandler

import datetime


def get_logger(name='tools', component='unknown'):
    """
    :return: Logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        syslog_handler = SysLogHandler(address=('syslog', 601))
        syslog_handler.setFormatter(JsonFormatter(component=component))
        logger.addHandler(syslog_handler)

    return logger


class JsonFormatter(logging.Formatter):
    def __init__(self, component=None):
        self.component = component
        super(JsonFormatter, self).__init__()

    def format(self, record):
        log_record = {
            'application': record.name,
            'timestamp': datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f'),
            'component': self.component,
            'level': record.levelname,
            'message': record.msg,
            'data': record.args
        }

        return log_record['application'] + ': ' + json.dumps(log_record)
