import logging
import os, sys


def get_error_info():
    exc_type, exc_obj, exc_tb = sys.exc_info()
    file_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    return file_name, exc_tb.tb_lineno


class Singleton:
    _instances = {}

    def __init__(self, class_):
        self._class_ = class_

    def __call__(self, *args, **kwargs):
        if self._class_ not in self._instances:
            self._instances[self._class_] = self._class_(*args, **kwargs)
        return self._instances[self._class_]


def create_logger(name, level=logging.INFO):
    logging.basicConfig(level=level,
                        format='[%(asctime)s][%(threadName)s : %(filename)s: %(lineno)d] %(levelname)s - %(message)s'
                        )
    _logger = logging.getLogger(name)
    _logger.info(f"DEBUG Level set: {level}")
    return _logger


__all__ = [
    'Singleton',
    'get_error_info',
    'create_logger'
]
