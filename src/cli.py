# -*- coding: utf-8 -*-

import argparse
import time
import schedule
from datetime import datetime
from engine import ResultInterface
from logger import Logger
from config import LINUX_USING_CRON_TIME_SCHEDULER, POLL_HL7BD_EVERY
from helpers import is_linux


logger = Logger(__name__, __file__)


def commence_raw():
    ResultInterface().run()


def commence_scheuled():
    # run now and schedule the nest jobs
    commence_raw()
    schedule.every(POLL_HL7BD_EVERY).minutes.do(commence_raw)

    while True:
        schedule.run_pending()
        time.sleep(10)


def main():

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        "-r",
        "--run",
        action="store_true",
        help="Start result forwarding ..."
    )

    args = parser.parse_args()

    # Start result forwarding ...
    if args.run:
        time_start = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.log("info", f"Starting interface transmission: {time_start}")

        if is_linux:
            if LINUX_USING_CRON_TIME_SCHEDULER:
                commence_raw()
            else:
                commence_scheuled()
        else:
            commence_scheuled()
