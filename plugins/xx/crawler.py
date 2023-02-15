import logging
import re


import bs4
import cfscrape

from retrying import retry

from plugins.xx.exceptions import TopRankNotFundError, JavBusPageError
from plugins.xx.utils import *
from plugins.xx.models import Course, Teacher

_LOGGER = logging.getLogger(__name__)





class JavLibrary:
    host: str = 'https://www.javlibrary.com'
    top20_url: str = f'{host}/cn/vl_mostwanted.php?page=1'
    cookie: str
    ua: str
    proxies: dict
    cookie_dict: dict
    headers: dict
    scraper = cfscrape.create_scraper()

    def __init__(self, cookie: str = '', ua: str = '', proxies: dict = None):
        self.cookie = cookie
        self.ua = ua
        self.proxies = proxies
        self.cookie_dict = str_cookies_to_dict(cookie)
        self.headers = {'cookie': cookie, 'Referer': self.host}
        if ua:
            self.headers['User-Agent'] = ua

    @retry(stop_max_attempt_number=4, wait_fixed=3)
    def crawling_top20(self):
        code_list = []
        res = self.scraper.get(url=self.top20_url, proxies=self.proxies, cookies=self.cookie_dict, headers=self.headers)
        soup = bs4.BeautifulSoup(res.text, 'html.parser')
        page_title = soup.select_one('head>title').text
        if page_title.startswith('最想要的影片'):
            videos = soup.select('div.video>a')
            if videos:
                for video in videos:
                    code = video.select_one('a div.id').text
                    code_list.append(code)
                return code_list
            else:
                raise TopRankNotFundError
        else:
            raise TopRankNotFundError


class JavBus:
    hosts: List = ['https://www.javbus.com', 'https://www.javsee.bar', 'https://www.seejav.icu',
                   'https://www.javsee.in']
    rotate_index = 0
    cookie: str
    ua: str
    proxies: dict
    cookie_dict: dict
    headers: dict
    scraper = cfscrape.create_scraper()

    def __init__(self, cookie: str = '', ua: str = '', proxies: dict = None):
        self.cookie = cookie
        self.ua = ua
        self.proxies = proxies
        if 'existmag' not in self.cookie:
            self.cookie = f"existmag=all; {self.cookie}"
        else:
            self.cookie = self.cookie.replace('existmag=mag', 'existmag=all')
        self.cookie_dict = str_cookies_to_dict(cookie)
        self.headers = {'cookie': cookie, 'Referer': self.hosts[0]}
        if ua:
            self.headers['User-Agent'] = ua

    def rotate_host(self) -> str:
        current_index = self.rotate_index
        if self.rotate_index == len(self.hosts) - 1:
            self.rotate_index = 0
        else:
            self.rotate_index = self.rotate_index + 1
        return self.hosts[current_index]

    @retry(stop_max_attempt_number=4, wait_fixed=3)
    def search_code(self, code):
        url = f"{self.rotate_host()}/{code}"
        res = self.scraper.get(url=url, proxies=self.proxies, headers=self.headers, cookies=self.cookie_dict)
        soup = bs4.BeautifulSoup(res.text, 'html.parser')
        page_title = soup.select_one('head>title').text
        if page_title.startswith('404'):
            return None
        if page_title.startswith(code):
            info = soup.select_one('div.info')
            if info:
                release_date = ''
                duration = ''
                producer = ''
                publisher = ''
                series = ''
                genre_list = ''
                cast_list = ''
                title = soup.select_one('h3').text
                release_date_element = info.find('span', text='發行日期:')
                duration_element = info.find('span', text='長度:')
                producer_element = info.find('span', text='製作商:')
                publisher_element = info.find('span', text='發行商:')
                series_element = info.find('span', text='系列:')
                genre_elements = info.select('span.genre>label>a')
                cast_elements = info.select('div.star-box>li>div.star-name>a')
                banner = soup.select_one('a.bigImage>img').get('src')
                poster = banner.replace('cover', 'thumb').replace('_b', '')
                if release_date_element:
                    release_date = release_date_element.parent.contents[1].text.strip()
                if duration_element:
                    duration = duration_element.parent.contents[1].text.strip().replace('分鐘', '')
                if producer_element:
                    producer = producer_element.parent.find('a').text.strip()
                if publisher_element:
                    publisher = publisher_element.parent.find('a').text.strip()
                if series_element:
                    series = series_element.parent.find('a').text.strip()
                if genre_elements:
                    genre_list = [item.text for item in genre_elements]
                if cast_elements:
                    cast_list = [item.get('title') for item in cast_elements]
                course = Course({'code': code, 'title': title, 'release_date': release_date, 'duration': duration,
                                 'producer': producer, 'publisher': publisher,
                                 'series': series, 'genres': ','.join(genre_list), 'casts': ','.join(cast_list),
                                 'poster': poster, 'banner': banner})
                return course
            return None
        else:
            raise JavBusPageError

    @retry(stop_max_attempt_number=4, wait_fixed=3)
    def search_teacher(self, keyword):
        if len(keyword) == len(keyword.encode()) and has_number(keyword):
            true_code = get_true_code(keyword)
            teacher_code_list = self.get_teachers(true_code)
            teacher_num = len(teacher_code_list)
            if teacher_num != 1:
                return None
            teacher_code = teacher_code_list[0]
        else:
            teacher_code = self.search_by_name(keyword)
        if teacher_code:
            teacher = self.crawling_teacher(teacher_code)
            return teacher
        return None

    @retry(stop_max_attempt_number=4, wait_fixed=3)
    def crawling_teacher(self, teacher_code):
        url = f"{self.rotate_host()}/star/{teacher_code}"
        res = self.scraper.get(url=url, proxies=self.proxies, headers=self.headers, cookies=self.cookie_dict)
        soup = bs4.BeautifulSoup(res.text, 'html.parser')
        page_title = soup.select_one('head>title').text
        if page_title.startswith('404'):
            return None
        if page_title.endswith('女優 - 影片'):
            photo_info = soup.select_one('div.photo-info')
            if photo_info:
                photo = ''
                name = ''
                birth = ''
                height = ''
                cup = ''
                bust = ''
                waist = ''
                hip = ''
                photo_element = soup.select_one('div.photo-frame>img')
                name_element = photo_info.select_one('span')
                birth_element = photo_info.find('p', text=re.compile('生日*'))
                height_element = photo_info.find('p', text=re.compile('身高*'))
                cup_element = photo_info.find('p', text=re.compile('罩杯*'))
                bust_element = photo_info.find('p', text=re.compile('胸圍*'))
                waist_element = photo_info.find('p', text=re.compile('腰圍*'))
                hip_element = photo_info.find('p', text=re.compile('臀圍*'))
                if photo_element:
                    photo = photo_element.get('src')
                if name_element:
                    name = name_element.text
                if birth_element:
                    birth = birth_element.text.replace('生日:', '').strip()
                if height_element:
                    height = height_element.text.replace('身高:', '').strip()
                if cup_element:
                    cup = cup_element.text.replace('罩杯:', '').strip()
                if bust_element:
                    bust = bust_element.text.replace('胸圍:', '').strip()
                if waist_element:
                    waist = waist_element.text.replace('腰圍:', '').strip()
                if hip_element:
                    hip = hip_element.text.replace('臀圍:', '').strip()
                teacher = Teacher(
                    {'code': teacher_code, 'photo': photo, 'name': name, 'birth': birth, 'height': height, 'cup': cup,
                     'bust': bust, 'waist': waist, 'hip': hip})
                return teacher
            return None
        else:
            raise JavBusPageError

    @retry(stop_max_attempt_number=4, wait_fixed=3)
    def crawling_teacher_courses(self, teacher_code, limit_date):
        start_date_timestamp = date_str_to_timestamp(limit_date)
        print(start_date_timestamp)
        if not start_date_timestamp:
            return None
        url = f"{self.rotate_host()}/star/{teacher_code}"
        res = self.scraper.get(url=url, proxies=self.proxies, headers=self.headers, cookies=self.cookie_dict)
        soup = bs4.BeautifulSoup(res.text, 'html.parser')
        page_title = soup.select_one('head>title').text
        if page_title.startswith('404'):
            return []
        if page_title.endswith('女優 - 影片'):
            movie_list = soup.select('a.movie-box')
            code_list = []
            for item in movie_list:
                date_list = item.select('date')
                code_list.append({'date': date_list[1].text, 'code': date_list[0].text})
            filter_list = list(
                filter(
                    lambda x: date_str_to_timestamp(x['date']) >= start_date_timestamp,
                    code_list))
            new_list = []
            for item in filter_list:
                teacher_list = self.get_teachers(item['code'])
                teacher_num = None
                if teacher_list:
                    teacher_num = len(teacher_list)
                if teacher_num and teacher_num < 4:
                    new_list.append(item['code'])
            return new_list
        else:
            raise JavBusPageError

    @retry(stop_max_attempt_number=4, wait_fixed=3)
    def get_teachers(self, code: str):
        url = f"{self.rotate_host()}/{code}"
        res = self.scraper.get(url=url, proxies=self.proxies, headers=self.headers, cookies=self.cookie_dict)
        soup = bs4.BeautifulSoup(res.text, 'html.parser')
        page_title = soup.select_one('head>title').text
        if page_title.startswith('404'):
            return []
        if page_title.startswith(code):
            casts_list = soup.select('div.info>ul>div.star-box>li>div.star-name>a')
            teacher_code_list = []
            if casts_list:
                for cast in casts_list:
                    url = cast.get('href')
                    code_split_list = url.split('/')
                    code = code_split_list[len(code_split_list) - 1]
                    teacher_code_list.append(code)
            return teacher_code_list
        else:
            raise JavBusPageError

    @retry(stop_max_attempt_number=4, wait_fixed=3)
    def search_by_name(self, teacher_name):
        url = f"{self.rotate_host()}/searchstar/{teacher_name}"
        res = self.scraper.get(url=url, proxies=self.proxies, headers=self.headers, cookies=self.cookie_dict)
        soup = bs4.BeautifulSoup(res.text, 'html.parser')
        page_title = soup.select_one('head>title').text
        if page_title == '搜尋 - 女優列表 - JavBus - JavBus':
            actors = soup.select('a.avatar-box')
            if len(actors) != 1:
                return None
            teacher_url = actors[0].get('href')
            code_split_list = teacher_url.split('/')
            code = code_split_list[len(code_split_list) - 1]
            return code
        elif page_title.startswith('沒有您要的結果！'):
            return None
        else:
            raise JavBusPageError

    @retry(stop_max_attempt_number=4, wait_fixed=3)
    def search_all_by_name(self, teacher_name):
        url = f"{self.rotate_host()}/searchstar/{teacher_name}"
        res = self.scraper.get(url=url, proxies=self.proxies, headers=self.headers, cookies=self.cookie_dict)
        soup = bs4.BeautifulSoup(res.text, 'html.parser')
        page_title = soup.select_one('head>title').text
        teacher_code_List = []
        if page_title == '搜尋 - 女優列表 - JavBus - JavBus':
            actors = soup.select('a.avatar-box')
            for actor in actors:
                teacher_url = actor.get('href')
                code_split_list = teacher_url.split('/')
                code = code_split_list[len(code_split_list) - 1]
                teacher_code_List.append(code)
            return teacher_code_List
        elif page_title.startswith('沒有您要的結果！'):
            return None
        else:
            raise JavBusPageError
