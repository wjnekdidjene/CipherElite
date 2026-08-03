import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from colorama import init, Fore, Style

init(autoreset=True)


class ColoredFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Style.BRIGHT
    }

    def format(self, record):
        color = self.COLORS.get(record.levelname, Fore.WHITE)
        record.levelname = f"{color}{record.levelname}{Style.RESET_ALL}"
        return super().format(record)


def setup_logging(name: str = "CipherElite"):
    Path("logs").mkdir(exist_ok=True)
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(ColoredFormatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    ))
    logger.addHandler(console)

    file = RotatingFileHandler(
        'logs/cipher.log',
        maxBytes=5*1024*1024,
        backupCount=3
    )
    file.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    logger.addHandler(file)

    return logger


def get_logger(name: str = "CipherElite"):
    return logging.getLogger(name)