import random
import time
import requests
import bs4
from qbittorrent import Client
from mbot.openapi import mbot_api
from mbot.core.plugins import *
from typing import Dict, Any
import logging
from .sql import *

_LOGGER = logging.getLogger(__name__)
server = mbot_api

path = ''
proxies = {
    'http': '',
    'https': '',
}
torrent_folder = '/data/plugins/jav_bot/torrents'
jav_cookie = ''
ua = ''
qb_url = None
qb_username = None
qb_password = None
category = None
qb = None


@plugin.after_setup
def after_setup(plugin_meta: PluginMeta, config: Dict[str, Any]):
    global path, proxies, torrent_folder, qb_url, qb_username, qb_password, jav_cookie, ua, category
    if config.get('path'):
        path = config.get('path')
    if config.get('proxy'):
        proxies = {
            'http': config.get('proxy'),
            'https': config.get('proxy')
        }
    if config.get('qb_url'):
        qb_url = config.get('qb_url')
    if config.get('username'):
        qb_username = config.get('username')
    if config.get('password'):
        qb_password = config.get('password')
    if config.get('jav_cookie'):
        jav_cookie = config.get('jav_cookie')
    if config.get('ua'):
        ua = config.get('ua')
    if config.get('category'):
        category = config.get('category')


@plugin.config_changed
def config_changed(config: Dict[str, Any]):
    global path, proxies, torrent_folder, qb_url, qb_username, qb_password, jav_cookie, ua, category
    if config.get('path'):
        path = config.get('path')
    if config.get('proxy'):
        proxies = {
            'http': config.get('proxy'),
            'https': config.get('proxy')
        }
    if config.get('qb_url'):
        qb_url = config.get('qb_url')
    if config.get('username'):
        qb_username = config.get('username')
    if config.get('password'):
        qb_password = config.get('password')
    if config.get('jav_cookie'):
        jav_cookie = config.get('jav_cookie')
    if config.get('ua'):
        ua = config.get('ua')
    if config.get('category'):
        category = config.get('category')


@plugin.task('task', '定时任务', cron_expression='0 22 * * *')
def task():
    time.sleep(random.randint(1, 3600))
    if login_qb():
        save_new_code()
        main()
    else:
        _LOGGER.error('QB登录失败')


def command():
    if login_qb():
        save_new_code()
        main()
        _LOGGER.error("精品科目,执行结束")
    else:
        _LOGGER.error('QB登录失败')


def download_by_code(code):
    if login_qb():
        chapter = get_chapter(code)
        if not chapter:
            chapter = {
                'code': code,
                'overview': '手动添加科目，无法获取简介',
                'img': ''
            }
            save_chapter(chapter)
        chapter = get_chapter(code)
        if chapter['status'] == 1:
            return '你已经下载过该科目'

        torrents = grab_m_team(code)
        if torrents:
            torrent = get_best_torrent(torrents)
            torrent_path = download_torrent(code, torrent['download_url'])
            res = download(torrent_path)
            if res == 'Ok.':
                chapter['size'] = torrent['size']
                chapter['download_url'] = torrent['download_url']
                chapter['download_path'] = path
                update_chapter(chapter)
                return '已开始下载该科目的资源'
            else:
                return '添加种子下载失败'
        else:
            return '没用找到该科目的资源,已保存到想看的科目列表'
    else:
        _LOGGER.error('QB登录失败')


def login_qb():
    global qb
    qb = Client(qb_url)
    res = qb.login(qb_username, qb_password)
    if res:
        return False
    return True


def save_new_code():
    av_list = grab_jav(1)
    if not av_list:
        _LOGGER.error('爬取jav失败')
        return
    for av in av_list:
        code = av['code']
        overview = av['overview']
        img = av['img']
        chapter = get_chapter(code)
        if not chapter:
            chapter = {
                'code': code,
                'overview': overview,
                'img': img
            }
            save_chapter(chapter)


def main():
    cookies = get_m_team_cookie()
    if not cookies:
        _LOGGER.error('尚未配置馒头站点')
        return
    chapters = list_un_download_chapter()
    _LOGGER.info("尚未下载的科目:")
    _LOGGER.info([chapter['chapter_code'] for chapter in chapters])
    for chapter in chapters:
        code = chapter['chapter_code']
        torrents = grab_m_team(code)
        if torrents:
            torrent = get_best_torrent(torrents)
            if torrent:
                torrent_path = download_torrent(code, torrent['download_url'])
                res = download(torrent_path)
                if res == 'Ok.':
                    chapter['size'] = torrent['size']
                    chapter['download_url'] = torrent['download_url']
                    chapter['download_path'] = path
                    update_chapter(chapter)
                else:
                    _LOGGER.error('添加种子到下载器出错')
            else:
                _LOGGER.info("未找到有效种子")
        else:
            _LOGGER.info("尚无资源")
        _LOGGER.info("等待10-20S继续操作")
        time.sleep(random.randint(10, 20))


def grab_m_team(keyword):
    url = f'https://kp.m-team.cc/adult.php?incldead=1&spstate=0&inclbookmarked=0&search={keyword}&search_area=0&search_mode=0'
    m_team_cookies = get_m_team_cookie()
    user_agent = get_m_team_ua()
    cookie_str = get_m_team_cookie_str()
    headers = {'cookie': cookie_str, 'Referer': "https://kp.m-team.cc"}
    if user_agent:
        headers['User-Agent'] = user_agent
    res = requests.get(url, cookies=m_team_cookies, headers=headers)
    _LOGGER.info(res.text)
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
        weight = get_weight(title, describe, int(seeders))
        torrent['weight'] = weight
        torrents.append(torrent)
    return torrents


def grab_jav(page):
    url = f'https://www.javlibrary.com/cn/vl_mostwanted.php?page={page}'
    av_list = []
    cookie_dict = str_cookies_to_dict(jav_cookie)
    headers = {'cookie': jav_cookie, 'Referer': "https://www.javlibrary.com"}
    if ua:
        headers['User-Agent'] = ua
    res = requests.get(url=url, proxies=proxies, cookies=cookie_dict, headers=headers)
    _LOGGER.info(res.text)
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


def get_weight(title: str, describe: str, seeders: int):
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
    return weight


def get_best_torrent(torrents):
    if torrents:
        sort_list = sorted(torrents, key=lambda torrent: torrent['weight'], reverse=True)
        torrent = sort_list[0]
        if torrent['weight'] < 0:
            return None
        return torrent
    return None


def download_torrent(code, download_url):
    host = 'https://kp.m-team.cc/'
    cookies = get_m_team_cookie()
    res = requests.get(host + download_url, cookies=cookies)
    folder = torrent_folder
    torrent_path = f'{folder}/{code}.torrent'

    with open(torrent_path, 'wb') as torrent:
        torrent.write(res.content)
        torrent.flush()
    return torrent_path


def download(torrent_path):
    torrent_file = open(torrent_path, 'rb')
    return qb.download_from_file(torrent_file, savepath=path, category=category)


def get_m_team_ua():
    site_list = server.site.list()
    ssd_list = list(
        filter(lambda x: x.site_id == 'mteam', site_list))
    if len(ssd_list) > 0:
        ssd = ssd_list[0]
        user_agent = ssd.user_agent
        return user_agent
    return None


def get_m_team_cookie_str():
    site_list = server.site.list()
    ssd_list = list(
        filter(lambda x: x.site_id == 'mteam', site_list))
    if len(ssd_list) > 0:
        ssd = ssd_list[0]
        cookies = ssd.cookie
        return cookies
    return None


def get_m_team_cookie():
    cookie_str = get_m_team_cookie_str()
    if cookie_str:
        dict_cookie = str_cookies_to_dict(cookie_str)
        return dict_cookie
    return None


def str_cookies_to_dict(cookies):
    dict_cookie = {}
    str_cookie_list = cookies.split(';')
    for cookie in str_cookie_list:
        if cookie.strip(' '):
            cookie_key_value = cookie.split('=')
            key = cookie_key_value[0]
            value = cookie_key_value[1]
            dict_cookie[key] = value
    return dict_cookie
