import logging
from typing import Dict, Any

from moviebotapi.site import SearchQuery, SearchType, CateLevel1

from mbot.common.numberutils import NumberUtils
from mbot.core.plugins import plugin, PluginMeta
from plugins.xx.site import *
from mbot.openapi import mbot_api
from plugins.xx.orm import ConfigDB, DB

_LOGGER = logging.getLogger(__name__)

db = DB()
config_db = ConfigDB(db.session)





@plugin.after_setup
def after_setup(plugin_meta: PluginMeta, config: Dict[str, Any]):
    for torrent in torrents:
        _LOGGER.error(torrent.name)



