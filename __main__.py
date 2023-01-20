import time
import os
import sys
from datetime import datetime
from engine import ResultInterface
from logger import setup_logs_dirs, Logger
from config import LINUX_USING_CRON_TIME_SCHEDULER, POLL_HL7BD_EVERY

setup_logs_dirs()
logger = Logger(__name__, __file__)


def is_linux():
    return sys.platform == 'linux' or sys.platform.startswith('linux') or os.name == 'posix'


def is_windows():
    return sys.platform == 'win32' or sys.platform.startswith('win') or os.name == 'nt'


def commence_raw():
    ResultInterface().run()


def commence_scheuled():
    import schedule

    # run now and schedule the nest jobs
    commence_raw()
    schedule.every(POLL_HL7BD_EVERY).minutes.do(commence_raw)

    while True:
        schedule.run_pending()
        time.sleep(10)


if __name__ == '__main__':
    time_start = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.log("info", f"Starting interface transmission: {time_start}")

    if is_linux:
        if LINUX_USING_CRON_TIME_SCHEDULER:
            commence_raw()
        else:
            commence_scheuled()
    else:
        commence_scheuled()

    time_end = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.log("info", f"Finished interface transmission: {time_end}")
