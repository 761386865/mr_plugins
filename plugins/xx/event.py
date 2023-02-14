import logging
from typing import Dict, Any

from mbot.core.plugins import plugin, PluginMeta
from plugins.xx.site import *

_LOGGER = logging.getLogger(__name__)


@plugin.after_setup
def after_setup(plugin_meta: PluginMeta, config: Dict[str, Any]):
    torrents = search_torrent_by_code('ABW-302')
    for torrent in torrents:
        _LOGGER.error(torrent.name)
