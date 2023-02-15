import logging
from typing import List

from moviebotapi.site import SearchQuery, SearchType, CateLevel1, Torrent

from mbot.common.numberutils import NumberUtils
from plugins.xx.exceptions import ConfigInitError
from plugins.xx.models import Config
from plugins.xx.site import *
from mbot.openapi import mbot_api
from plugins.xx.orm import ConfigDB, DB

_LOGGER = logging.getLogger(__name__)

db = DB()
config_db = ConfigDB(db.session)


class Site:
    config: Config
    cn_keywords = ['中字', '中文字幕', '色花堂', '字幕'],

    def __int__(self, config: Config):
        if not config:
            _LOGGER.error("请先初始化配置")
            raise ConfigInitError
        if not config.site_id:
            return []
        self.config = config

    def get_torrent(self, code):
        torrents = self.search_torrents(code)
        filter_torrents = self.filter_torrents(torrents)
        sort_torrents = self.sort_torrents(filter_torrents)
        if sort_torrents:
            return sort_torrents[0]

    def search_torrents(self, code):
        query = SearchQuery(SearchType.Keyword, code)
        return mbot_api.site.search_remote(query=query, cate_level1=[CateLevel1.AV],
                                           site_id=self.config.site_id.split(','))

    def filter_torrents(self, torrents: List[Torrent]):
        only_chinese = self.config.only_chinese
        max_size = self.config.max_size
        min_size = self.config.min_size
        filter_list = []
        for torrent in torrents:
            title = torrent.name + torrent.subject
            size_mb = torrent.size_mb
            if only_chinese:
                has_chinese = self.has_chinese(title)
                setattr(torrent, 'chinese', has_chinese)
                if not has_chinese:
                    continue
            if max_size:
                if size_mb > max_size:
                    continue
                if size_mb < min_size:
                    continue
            filter_list.append(torrent)
        return filter_list

    @staticmethod
    def sort_torrents(torrents: List[Torrent]):
        upload_sort_list = sorted(torrents, key=lambda torrent: torrent.upload_count, reverse=True)
        cn_sort_list = sorted(upload_sort_list, key=lambda torrent: torrent.chinese, reverse=True)
        return cn_sort_list

    def has_chinese(self, title):
        has_chinese = False
        for keyword in self.cn_keywords:
            if title.find(keyword) > -1:
                has_chinese = True
                break
        return has_chinese
