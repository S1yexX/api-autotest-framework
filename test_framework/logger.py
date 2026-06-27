import logging
import os
from datetime import datetime

LOG_DIR: str = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

log_file: str = os.path.join(LOG_DIR, f"api_{datetime.now().strftime('%Y%m%d')}.log")
log_format: str = "%(asctime)s - %(levelname)s - %(message)s"

file_handler: logging.FileHandler = logging.FileHandler(log_file, encoding="utf-8")
console_handler: logging.StreamHandler = logging.StreamHandler()

logging.basicConfig(
    level=logging.INFO,
    format=log_format,
    handlers=[file_handler, console_handler],
)

logger: logging.Logger = logging.getLogger("api_test")


def log_http(msg: str) -> None:
    """统一打印HTTP接口日志"""
    logger.info(msg)
