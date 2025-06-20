import logging
from logging.handlers import RotatingFileHandler
from os.path import join
from os import makedirs
from functools import lru_cache

def setup_logger(name:str, logs_dir:str) -> logging.Logger:
    """
    Setup logger
    Logs will be saved to `logs/{name} app.log`
    After ~5MB, it rolls over to `app.log.1`, `app.log.2`, etc.
    After 3 files, the oldest gets deleted

    Args:
        name (str): Name of the logger
        logs_dir (str): Directory to save logs

    Returns:
        logging.Logger
    """

    logger = logging.getLogger(name)
    if not logger.handlers: add_log_handlers(logger, name, logs_dir)

    return logger
    
def add_log_handlers(logger:logging.Logger, name:str, logs_dir:str) -> logging.Logger:
    logger.setLevel(logging.INFO)

    # Ensure logs directory exists
    makedirs(logs_dir, exist_ok=True)

    # Define log format
    LOG_FORMAT = "[%(asctime)s] [%(levelname)s] %(filename)s:%(funcName)s:%(lineno)d - %(message)s"
    formatter = logging.Formatter(
        LOG_FORMAT,
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Define log handlers
    log_handler = RotatingFileHandler(
        filename= join(logs_dir, f"{name}.log"),
        maxBytes= 5 * 1024 * 1024,  # 5 MB
        backupCount=3,              # Keep latest 3 log files
        encoding= 'utf-8'
    )
    log_handler.setFormatter(formatter)

    # Optional: also log to console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # Add handlers
    logger.addHandler(log_handler)
    logger.addHandler(console_handler)

    return logger

@lru_cache
def get_logger(name:str = "BrainAspire", logs_dir:str = "app/logs") -> logging.Logger:
    """
    Get or create a logger instance.
    
    Args:
        name (str): Name of the logger
        logs_dir (str): Directory to save logs
    
    Returns:
        logging.Logger: Configured logger instance
    """
    return setup_logger(name, logs_dir)