# coding:utf-8

import os
import logging
import json
import datetime
import traceback
import logging.config
import sys
from flask.logging import default_handler
from service import app
from pathlib import Path


class RobustFormatter(logging.Formatter):
    """
    Display Json format. The Json includes: { message, extra args }
    Regarding to exception, it will display few info (exception name, location, etc.)
    """

    def format(self, record):
        extra = record.__dict__
        record.message = record.getMessage()
        if self.usesTime():
            record.asctime = self.formatTime(record, self.datefmt)
        s = self.formatMessage(record)
        if record.exc_info:
            # Other formater will use the exception info, so don't cache it in
            # record.exc_text
            exc_text = self.formatException(record.exc_info)
            if s[-1:] != "\n":
                s = s + "\n"
            s = exc_text + s

        s = {
            "action": extra.get("action", "undefined"),
            "message": s,
            "process": extra.get("process", "undefined"),
            '@timestamp': datetime.datetime.utcnow().strftime(
                '%Y-%m-%dT%H:%M:%S.%fZ'),
            'levelname': extra.get("levelname", "undefined"),
        }
        if "schema" in extra:
            s["schema"] = extra["schema"]
        return json.dumps(s)

    def formatException(self, ei):
        type, value, tb = ei
        r = traceback.extract_tb(tb, limit=None)[-1]
        s = "Exception in file {} line {}, Reason: {} Message: ".format(
            r.filename, r.lineno, value)
        return s

from logging.handlers import WatchedFileHandler

class MyFileHandler(WatchedFileHandler):
    def __init__(self, filename, mode='a', encoding=None, delay=False):
        WatchedFileHandler.__init__(self, filename, mode, encoding, delay)

    def emit(self, record):
        if not record.levelno == self.level:
            return
        WatchedFileHandler.emit(self, record)

def get_logger_settings(log_dir, console_output=True):
    logger_settings = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            # For Normal log, info, debug, error...
            'logstash_log': {
                '()': "loggin.logger.RobustFormatter"
            },
            'fmt': {
                'format': ('[%(asctime) - 6s]: %(name)s - %(levelname)s - '
                           '%(filename)s - %(funcName)s :\n'
                           '%(message)s;'),
                'datefmt': "%Y-%m-%d %H:%M:%S",
            }
        },
        'handlers': {
            'console': {
                'level': 'INFO',
                'class': 'logging.StreamHandler',
                'formatter': 'fmt',
                'stream': sys.stdout,
            },
            'info_file': {
                'level': 'INFO',
                'class': 'loggin.logger.MyFileHandler',
                'formatter': 'fmt',
                'filename': os.path.join(log_dir, 'info.log'),
            },
            'debug_file': {
                'level': 'DEBUG',
                'class': 'loggin.logger.MyFileHandler',
                'formatter': 'fmt',
                'filename': os.path.join(log_dir, 'debug.log'),
            },
            'error_file': {
                'level': 'ERROR',
                'class': 'loggin.logger.MyFileHandler',
                'formatter': 'fmt',
                'filename': os.path.join(log_dir, 'error.log'),
            },
        },
        'loggers': {
            'service': {
                'level': 'INFO',
                'handlers': ['info_file', 'debug_file', 'error_file'],
                'propagate': False
            }
        },
        'root': {
            'handlers': ['info_file', 'debug_file', 'error_file'],
            'level': 'INFO',
            'propagate': False
        }
    }
    if console_output:
        logger_settings["root"]["handlers"].insert(0, "console")
        logger_settings["loggers"]["service"]["handlers"].insert(0, "console")
    return logger_settings

# Setting up Logger


def initialize_logging(log_level=logging.INFO):
    """ Initialized the default logging to STDOUT """
    print('Setting up logging...')
    handler_list = list(app.logger.handlers)
    for log_handler in handler_list:
        app.logger.removeHandler(log_handler)
    dir_name, file_name = os.path.split(os.path.abspath(__file__))
    log_dir_name = os.path.join(str(Path(dir_name).parent),"data/log/")
    if os.path.exists(log_dir_name) == False:
        os.mkdir(str(Path(log_dir_name).parent))
        os.mkdir(log_dir_name)
    logging.config.dictConfig(get_logger_settings(log_dir_name, True))
    if not app.debug:
        # Set up default logging for submodules to use STDOUT
        # datefmt='%m/%d/%Y %I:%M:%S %p'
        app.logger.setLevel(log_level)
    else:
        app.logger.setLevel(logging.DEBUG)
    app.logger.info('Logging handler established')
