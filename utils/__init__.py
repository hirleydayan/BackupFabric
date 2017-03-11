"""Utils package funtions."""
import logging
import logging.handlers

# Color range
BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

# Control sequences
CRT_RESET = "\033[0m"
CRT_COLOR = "\033[1;%dm"
CRT_BOLD = "\033[1m"

# Log type and related collors
COLORS = {
    'WARNING': YELLOW,
    'INFO': BLUE,
    'DEBUG': MAGENTA,
    'CRITICAL': YELLOW,
    'ERROR': RED
}


def formatter_message(message):
    """The function replaces control texts by their respective sequences."""
    message = message.replace("$RESET", CRT_RESET)
    message = message.replace("$BOLD", CRT_BOLD)
    message = message.replace("$FG_BLACK", CRT_COLOR % (30 + GREEN))
    message = message.replace("$BG_BLACK", CRT_COLOR % (40 + GREEN))
    message = message.replace("$FG_RED", CRT_COLOR % (30 + RED))
    message = message.replace("$BG_RED", CRT_COLOR % (40 + RED))
    message = message.replace("$FG_GREEN", CRT_COLOR % (30 + GREEN))
    message = message.replace("$BG_GREEN", CRT_COLOR % (40 + GREEN))
    message = message.replace("$FG_YELLOW", CRT_COLOR % (30 + YELLOW))
    message = message.replace("$BG_YELLOW", CRT_COLOR % (40 + YELLOW))
    message = message.replace("$FG_BLUE", CRT_COLOR % (30 + BLUE))
    message = message.replace("$BG_BLUE", CRT_COLOR % (40 + BLUE))
    message = message.replace("$FG_MAGENTA", CRT_COLOR % (30 + MAGENTA))
    message = message.replace("$BG_MAGENTA", CRT_COLOR % (40 + MAGENTA))
    message = message.replace("$FG_CYAN", CRT_COLOR % (30 + CYAN))
    message = message.replace("$BG_CYAN", CRT_COLOR % (40 + CYAN))
    message = message.replace("$FG_WHITE", CRT_COLOR % (30 + WHITE))
    message = message.replace("$BG_WHITE", CRT_COLOR % (40 + WHITE))
    return message


class ColoredFormatter(logging.Formatter):
    """The ColoredFormater class."""

    def __init__(self, msg, use_color=True):
        """The init class function."""
        logging.Formatter.__init__(self, msg)
        self.use_color = use_color

    def format(self, record):
        """The format function."""
        levelname = record.levelname
        if self.use_color and levelname in COLORS:
            levelname_color = CRT_COLOR % (30 + COLORS[levelname]) + \
                levelname + CRT_RESET
            record.levelname = levelname_color
        return logging.Formatter.format(self, record)


def init_logger_with_rotate(filename, string):
    """The init logger function with file rotate."""
    logger = logging.getLogger()

    file_handler = logging.handlers.RotatingFileHandler(filename,
                                                        maxBytes=104857600,
                                                        backupCount=5)
    file_formater = logging.Formatter("[%(asctime)s] [" + string +
                                      "] [%(levelname)-.3s] : %(message)s",
                                      "%Y-%m-%d %H:%M:%S")
    file_handler.setFormatter(file_formater)
    logger.addHandler(file_handler)

    fmt_str = "[%(asctime)s] [$BOLD" + string + \
              "$RESET] [%(levelname)-18s] : $FG_CYAN%(message)s$RESET"

    color_format = formatter_message(fmt_str)
    color_formatter = ColoredFormatter(color_format)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(color_formatter)
    logger.addHandler(console_handler)

    logger.setLevel(logging.INFO)
    return logger


def init_config(config_file):
    """The init config function."""
    import ConfigParser
    config = ConfigParser.ConfigParser()
    config.read(config_file)
    return config


def cleanup_text(text, file_name_format=False):
    """The init config function."""
    import re
    if not (type(text) is str):
        return None
    text = text.strip()
    text = ' '.join(text.split())
    if file_name_format:
        text = '_'.join(re.split("[ ()!?:]+", text))
    return text
