import os
import sys
import logging

from mcpi2.constants import *

# Logger format string
logging_str = "[%(asctime)s: %(lineno)d: %(name)s: %(levelname)s: %(module)s:  %(message)s]"

# Define log directory and log file path
log_dir = os.path.join(PACKAGE_DIR, "logs")
log_file_path = os.path.join(log_dir, "running_logs.log")

# Check and create log directory if not exists
os.makedirs(log_dir, exist_ok=True)

# Basic logging configuration
logging.basicConfig(
    level=logging.INFO,
    format=logging_str,
    handlers=[
        logging.FileHandler(log_file_path),
        logging.StreamHandler(sys.stdout)
    ]
)

# Create and provide logger instance
logger = logging.getLogger("logger")