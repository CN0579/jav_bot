import datetime
import os.path
import time
from typing import List

import bs4
import requests
from mbot.openapi import mbot_api
from mbot.common.numberutils import NumberUtils


def str_cookies_to_dict(cookies):
    dict_cookie = {}
    str_cookie_list = cookies.split(';')
    for cookie in str_cookie_list:
        if cookie.strip(' '):
            cookie_key_value = cookie.split('=')
            if len(cookie_key_value) < 2:
                continue
            key = cookie_key_value[0]
            value = cookie_key_value[1]
            dict_cookie[key] = value
    return dict_cookie


class JavLibrary:
    host: str = 'https://www.javlibrary.com'
    top20_url: str = f'{host}/cn/vl_mostwanted.php?page=1'
    cookie: str
    ua: str
    proxies: dict
    cookie_dict: dict
    headers: dict

    def __init__(self, cookie: str, ua: str, proxies: dict = None):
        self.cookie = cookie
        self.ua = ua
        self.proxies = proxies
        self.cookie_dict = str_cookies_to_dict(cookie)
        self.headers = {'cookie': cookie, 'Referer': self.host}
        if ua:
            self.headers['User-Agent'] = ua

    def crawling_top20(self):
        av_list = []
        res = requests.get(url=self.top20_url, proxies=self.proxies, cookies=self.cookie_dict, headers=self.headers)
        soup = bs4.BeautifulSoup(res.text, 'html.parser')
        videos = soup.select('div.video>a')
        for video in videos:
            code = video.select('a div.id')[0].text
            img = video.find('img').get('src')
            overview = video.select('a div.title')[0].text
            av = {
                'code': code,
                'img': img,
                'overview': overview
            }
            av_list.append(av)
        return av_list


class MTeam:
    site_id: str = 'mteam'
    host: str = 'https://kp.m-team.cc'
    cookie: str
    ua: str
    cookie_dict: dict
    headers: dict
    torrent_folder: str = '/data/jav_bot_torrents'

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

    def crawling_torrents(self, keyword):
        url = f'{self.host}/adult.php?incldead=1&spstate=0&inclbookmarked=0&search={keyword}&search_area=0&search_mode=0'
        res = requests.get(url=url, cookies=self.cookie_dict, headers=self.headers)
        soup = bs4.BeautifulSoup(res.text, 'html.parser')
        trs = soup.select('table.torrents > tr:has(table.torrentname)')
        torrents = []
        for tr in trs:
            title = tr.select('a[title][href^="details.php?id="]')[0].get('title')
            download_url = tr.select('a[href^="download.php?id="]')[0].get('href')
            size = tr.select('td.rowfollow:nth-last-child(6)')[0].text
            seeders = tr.select('td.rowfollow:nth-last-child(5)')[0].text
            leechers = tr.select('td.rowfollow:nth-last-child(4)')[0].text
            describe_list = tr.select('table.torrentname > tr > td.embedded')[0].contents
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


class JavBus:
    hosts: List = ['https://www.javbus.com', 'https://www.javsee.bar', 'https://www.seejav.icu',
                   'https://www.javsee.in']
    cookie: str
    ua: str
    proxies: dict
    cookie_dict: dict
    headers: dict

    def __init__(self, cookie: str, ua: str, proxies: dict = None):
        self.cookie = cookie
        self.ua = ua
        self.proxies = proxies
        if 'exitmad' not in self.cookie:
            self.cookie = f"exitmad=all;{self.cookie}"
        else:
            self.cookie = self.cookie.replace('existmag=mag', 'existmag=all')
        self.cookie_dict = str_cookies_to_dict(cookie)
        self.headers = {'cookie': cookie, 'Referer': self.hosts[0]}
        if ua:
            self.headers['User-Agent'] = ua

    def crawling_actor(self, star_code, start_date: datetime.datetime):
        for host in self.hosts:
            url = f"{host}/star/{star_code}"
            try:
                res = requests.get(url=url, proxies=self.proxies, headers=self.headers, cookies=self.cookie_dict)
                break
            except Exception as e:
                continue
        if not res:
            return None
        soup = bs4.BeautifulSoup(res.text, 'html.parser')
        movie_list = soup.select('a.movie-box')
        code_list = []
        for item in movie_list:
            date_list = item.select('date')
            code_list.append({'date': date_list[1].text, 'code': date_list[0].text})
        start_date_timestamp = int(start_date.strftime('%Y%m%d'))
        filter_list = list(
            filter(
                lambda x: int(
                    datetime.datetime.strptime(x['date'], "%Y-%m-%d").strftime('%Y%m%d')) >= start_date_timestamp
                          and 'VR' not in x['code'],
                code_list))
        finally_list = []
        for item in filter_list:
            time.sleep(5)
            teacher_list = self.get_teacher_list(item['code'])
            teacher_num = None
            if teacher_list:
                teacher_num = len(teacher_list)
            if teacher_num and teacher_num < 4:
                finally_list.append(item)
        return finally_list

    def get_teacher_list(self, code: str):
        for host in self.hosts:
            url = f"{host}/{code}"
            try:
                res = requests.get(url=url, proxies=self.proxies, headers=self.headers, cookies=self.cookie_dict)
                break
            except Exception as e:
                continue
        if not res:
            return None
        soup = bs4.BeautifulSoup(res.text, 'html.parser')
        actor_list = soup.select('span.genre>a')
        if actor_list:
            teacher_list = []
            for actor in actor_list:
                name = actor.text
                url = actor.get('href')
                code_split_list = url.split('/')
                code = code_split_list[len(code_split_list) - 1]
                teacher_list.append({'teacher_name': name, 'teacher_code': code})
                return teacher_list
        return None

    def crawling_by_code(self, code):
        teacher_list = self.get_teacher_list(code)
        if teacher_list and len(teacher_list) == 1:
            teacher = teacher_list[0]
            return {'teacher_code': teacher['teacher_code'], 'teacher_name': teacher['teacher_name']}
        return None

    def crawling_by_name(self, teacher_name):
        for host in self.hosts:
            url = f"{host}/searchstar/{teacher_name}"
            try:
                res = requests.get(url=url, proxies=self.proxies, headers=self.headers, cookies=self.cookie_dict)
                break
            except Exception as e:
                continue
        if not res:
            return None
        soup = bs4.BeautifulSoup(res.text, 'html.parser')
        actors = soup.select('a.avatar-box')
        if len(actors) > 1:
            return None
        if len(actors) < 1:
            return None
        teacher_url = actors[0].get('href')
        code_split_list = teacher_url.split('/')
        code = code_split_list[len(code_split_list) - 1]
        teacher_name = actors[0].select('div.photo-frame>img')[0].get('title')
        return {'teacher_code': code, 'teacher_name': teacher_name}
