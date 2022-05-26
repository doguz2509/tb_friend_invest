import logging
import os
from typing import Callable, Optional

from aiogram import Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.utils.exceptions import NetworkError
from aiohttp import ClientOSError

try:
    from ..utils import Singleton
except (ImportError, ValueError, ModuleNotFoundError):
    from compose_folder.share_invest.utils import Singleton


logger = logging.getLogger(os.path.split(__file__)[-1])


@Singleton
class _service:
    network_retry = 10
    counter = 0

    def __init__(self, token=None):
        self._token = token
        self._bot: Optional[Bot] = None
        self._dp = None
        self._storage = MemoryStorage()
        self._on_startup = None
        self.skip_updates = True

    def set_on_startup(self, callback: Callable):
        self._on_startup = callback

    @property
    def token(self):
        return self._token

    @token.setter
    def token(self, token):
        self._token = token

    @property
    def bot(self):
        if not self._bot:
            self._bot = Bot(token=self._token)
        return self._bot

    @property
    def storage(self):
        return self._storage

    @property
    def dp(self):
        if not self._dp:
            self._dp = Dispatcher(self.bot, storage=self._storage)
        return self._dp

    def start(self, **kwargs):
        while True:
            try:
                if kwargs.get('token', None):
                    self.token = kwargs.get('token', None)
                logger.info(f"Starting bot for token: {self._token}")
                executor.start_polling(self.dp, skip_updates=self.skip_updates, on_startup=kwargs.get('start_up', []))
            except NetworkError as e:
                if self.counter > self.network_retry:
                    raise
                logging.warning(f"Cannot restart service for {self.counter} times; {e}")
                self.counter += 1
            except (KeyboardInterrupt, ClientOSError):
                logger.info(f"Stopping bot for token: {self._token}")
                break
            except Exception as e:
                logger.error(f"Start error: {e}")

    def stop(self):
        self.dp.stop_polling()


Service: _service = _service(os.getenv('TOKEN'))


__all__ = [
    'Service'
]
