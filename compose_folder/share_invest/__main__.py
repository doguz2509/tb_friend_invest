import os

try:
    from . import telegram_api
    from .telegram_api import handlers
    from . import utils
except (ImportError, ModuleNotFoundError):
    from compose_folder import telegram_api
    from telegram_api import handlers
    from compose_folder import utils


logger = None


if __name__ == '__main__':
    logger = utils.create_logger('ShareWithFriends', 'INFO')
    telegram_api.Service.start(token=os.getenv('TOKEN'))
