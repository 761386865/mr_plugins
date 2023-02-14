import os

import bs4
import cfscrape
import requests
from retrying import retry

from mbot.common.numberutils import NumberUtils
from mbot.openapi import mbot_api
from plugins.xx.utils import str_cookies_to_dict


class MTeam:
    site_id: str = 'mteam'
    host: str = 'https://kp.m-team.cc'
    cookie: str
    ua: str
    cookie_dict: dict
    headers: dict
    torrent_folder: str = '/data/jav_bot_torrents'
    scraper = cfscrape.create_scraper()

    def __init__(self):
        m_team = self.get_m_team()
        self.cookie = m_team.cookie
        self.ua = m_team.user_agent
        self.cookie_dict = str_cookies_to_dict(self.cookie)
        self.headers = {'cookie': self.cookie, 'Referer': self.host}
        if self.ua:
            self.headers['User-Agent'] = self.ua
        if not os.path.exists(self.torrent_folder):
            os.makedirs(self.torrent_folder)

    @retry(stop_max_attempt_number=3, wait_fixed=5)
    def crawling_torrents(self, keyword):
        url = f'{self.host}/adult.php?incldead=1&spstate=0&inclbookmarked=0&search={keyword}&search_area=0&search_mode=0'
        res = self.scraper.get(url=url, cookies=self.cookie_dict, headers=self.headers)
        soup = bs4.BeautifulSoup(res.text, 'html.parser')
        trs = soup.select('table.torrents > tr:has(table.torrentname)')
        torrents = []
        for tr in trs:
            title = tr.select_one('a[title][href^="details.php?id="]').get('title')
            download_url = tr.select_one('a[href^="download.php?id="]').get('href')
            size = tr.select_one('td.rowfollow:nth-last-child(6)').text
            seeders = tr.select_one('td.rowfollow:nth-last-child(5)').text
            leechers = tr.select_one('td.rowfollow:nth-last-child(4)').text
            describe_list = tr.select_one('table.torrentname > tr > td.embedded').contents
            describe = describe_list[len(describe_list) - 1].text

            torrent = {
                'title': title,
                'download_url': download_url,
                'size': size,
                'seeders': seeders,
                'leechers': leechers,
                'describe': describe
            }
            weight = self.get_weight(title, describe, int(seeders), size)
            torrent['weight'] = weight
            torrents.append(torrent)
        return torrents

    @staticmethod
    def get_weight(title: str, describe: str, seeders: int, size: str):
        cn_keywords = ['中字', '中文字幕', '色花堂', '字幕']
        weight = 0
        content = title + describe
        for keyword in cn_keywords:
            if content.find(keyword) > -1:
                weight = weight + 5000
                break
        weight = weight + seeders
        if seeders == 0:
            weight = -1
        mb_size = NumberUtils.trans_size_str_to_mb(size)
        if mb_size > 10240:
            weight = -1
        return weight

    @staticmethod
    def get_best_torrent(torrents):
        if torrents:
            sort_list = sorted(torrents, key=lambda torrent: torrent['weight'], reverse=True)
            torrent = sort_list[0]
            if torrent['weight'] < 0:
                return None
            return torrent
        return None

    def download_torrent(self, code, download_url):
        res = requests.get(f"{self.host}/{download_url}", cookies=self.cookie_dict)
        torrent_path = f'{self.torrent_folder}/{code}.torrent'
        with open(torrent_path, 'wb') as torrent:
            torrent.write(res.content)
            torrent.flush()
        return torrent_path

    def get_m_team(self):
        site_list = mbot_api.site.list()
        m_team_list = list(
            filter(lambda x: x.site_id == self.site_id, site_list))
        if len(m_team_list) > 0:
            m_team = m_team_list[0]
            return m_team
        return None
