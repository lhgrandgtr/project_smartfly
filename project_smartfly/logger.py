import os
import logging
import colorlog
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime

class CustomLogger:
    COLORS = {
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white',
    }

    def __init__(self, logger_name='SmartFly', log_dir='logs'):
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(logging.DEBUG)
        
        # Create logs directory if it doesn't exist
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # Create formatters
        console_formatter = colorlog.ColoredFormatter(
            '%(log_color)s[%(asctime)s] %(levelname)-8s%(reset)s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            log_colors=self.COLORS
        )
        
        file_formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)-8s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Console Handler with colors
        console_handler = colorlog.StreamHandler()
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

        # File Handler with rotation
        log_file = os.path.join(log_dir, f'{logger_name}_{datetime.now().strftime("%Y%m%d")}.log')
        file_handler = TimedRotatingFileHandler(
            log_file,
            when='midnight',
            interval=1,
            backupCount=7,  # Keep logs for 7 days
            encoding='utf-8'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)

# Create a default logger instance
logger = CustomLogger()

if __name__ == '__main__':
    # Example usage
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")