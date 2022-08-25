import sys

from logger.settings import LoguruHandler, logging_level_within

# Configuration
compression = 'zip'
log_format = '{level} {time} {name} {function}:{line}  {message}'
rotation = '1 week'

HANDLERS: list[LoguruHandler] = [
    LoguruHandler(
        {
            'sink': sys.stdout,
            'format': log_format,
            'level': 'INFO',
            'serialize': False,
        }
    ),
    LoguruHandler(
        {
            'sink': 'logs/debug.log',
            'format': log_format,
            'level': 'DEBUG',
            'rotation': rotation,
            'serialize': False,
            'compression': compression,
            'filter': lambda record: logging_level_within(record, ['DEBUG']),
        }
    ),
    LoguruHandler(
        {
            'sink': 'logs/info.log',
            'format': log_format,
            'level': 'INFO',
            'rotation': rotation,
            'serialize': False,
            'compression': compression,
            'filter': lambda record: logging_level_within(record, ['INFO', 'WARNING']),
        }
    ),
    LoguruHandler(
        {
            'sink': 'logs/error.log',
            'format': log_format,
            'level': 'ERROR',
            'rotation': rotation,
            'serialize': False,
            'compression': compression,
            'filter': lambda record: logging_level_within(record, ['ERROR', 'CRITICAL']),
        }
    ),
]
