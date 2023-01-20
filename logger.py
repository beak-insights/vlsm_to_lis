import logging
import os
from logging.handlers import RotatingFileHandler
import os
import sys

from config import BASE_DIR


def setup_logs_dirs():
    if not os.path.exists(os.path.join(BASE_DIR, 'logs')):
        os.makedirs(os.path.join(BASE_DIR, 'logs'))
        with open(os.path.join(BASE_DIR, 'logs', "messages.log"), "w") as f:
            f.write("")
        f.close()


class Logger():
    file_all = os.path.join(BASE_DIR, 'logs', 'messages.log')
    logging = logging

    def __init__(self, module_name, file_path):
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
