import asyncio
from datetime import datetime
from engine import ResultInterface
from logger import setup_logs_dirs, Logger

setup_logs_dirs()
logger = Logger(__name__, __file__)

if __name__ == '__main__':
    time_start = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.log("info", f"Starting interface transmission: {time_start}")
    asyncio.run(ResultInterface().run())
    time_end = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.log("info", f"Finished interface transmission: {time_end}")
