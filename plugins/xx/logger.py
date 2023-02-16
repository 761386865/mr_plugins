import logging
import inspect

_LOGGER = logging.getLogger(__name__)

plugin_name = '小姐姐订阅插件'


class Logger:

    @staticmethod
    def info(msg):
        filename = inspect.stack()[1].filename
        method = inspect.stack()[1].function
        lineno = inspect.stack()[1].lineno
        _LOGGER.info(f'[{plugin_name}] [{filename}] [{method}] [{lineno}行]:{msg}')

    @staticmethod
    def error(msg):
        filename = inspect.stack()[1].filename
        method = inspect.stack()[1].function
        lineno = inspect.stack()[1].lineno
        _LOGGER.error(f'[{plugin_name}] [{filename}] [{method}] [{lineno}行]:{msg}')

    @staticmethod
    def debug(msg):
        filename = inspect.stack()[1].filename
        method = inspect.stack()[1].function
        lineno = inspect.stack()[1].lineno
        _LOGGER.debug(f'[{plugin_name}] [{filename}] [{method}] [{lineno}行]:{msg}')
