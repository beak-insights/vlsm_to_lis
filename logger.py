
import sys
import os
import logging
from logging.handlers import RotatingFileHandler

from pathlib import Path
from helpers import is_linux, log_file_setup

log_file_path = Path(str(os.path.expanduser('~')) +
                     '\\Documents\\HL7DB-to-senaite\\logs\\')
log_file = Path(str(os.path.expanduser('~')) +
                '\\Documents\\HL7DB-to-senaite\\logs\\messages.log')

if is_linux():
    log_file_path = Path(str(os.path.expanduser('~')) +
                         '/Documents/HL7DB-to-senaite/logs/')
    log_file = Path(str(os.path.expanduser('~')) +
                    '/Documents/HL7DB-to-senaite/logs/messages.log')


class Logger():
    file_all = log_file
    logging = logging

    def __init__(self, module_name, file_path):
        log_file_setup(log_file_path, log_file)
        self.logging.getLogger(module_name)
        self.logging.basicConfig(
            handlers=[
                RotatingFileHandler(
                    self.file_all, maxBytes=100000000, backupCount=50),
                logging.StreamHandler(sys.stdout),
            ],
            # filename=self.file_all,
            level=logging.INFO,
            format='%(asctime)s — %(levelname)s - %(message)s',
            datefmt='%Y-%m/%dT%H:%M:%S',
        )
        self.module = module_name
        self.path = file_path

    def log(self, level, message:  str):
        level = level.upper()

        if level == "WARNING":
            self.logging.warning(message)
        elif level == "DEBUG":
            self.logging.debug(message)
        elif level == "ERROR":
            self.logging.error(message)
        elif level == "CRITICAL":
            self.logging.critical(message)
        else:
            self.logging.info(message)
