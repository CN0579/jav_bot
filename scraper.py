import datetime
import logging
import time

import bs4
import requests
from mbot.openapi import mbot_api
from mbot.common.numberutils import NumberUtils

_LOGGER = logging.getLogger(__name__)
server = mbot_api

jav_bus_urls = ['https://www.javbus.com', 'https://www.javsee.bar', 'https://www.seejav.icu', 'https://www.javsee.in']


def grab_jav(page, jav_cookie, ua, proxies):
    url = f'https://www.javlibrary.com/cn/vl_mostwanted.php?page={page}'
    av_list = []
    cookie_dict = str_cookies_to_dict(jav_cookie)
    headers = {'cookie': jav_cookie, 'Referer': "https://www.javlibrary.com"}
    if ua:
        headers['User-Agent'] = ua
    res = requests.get(url=url, proxies=proxies, cookies=cookie_dict, headers=headers)
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


def grab_jav_bus_by_code(code, jav_bus_cookie, ua, proxies):
    teacher_list = get_teacher_list(code, jav_bus_cookie, ua, proxies)
    if teacher_list and len(teacher_list) == 1:
        teacher = teacher_list[0]
        return {'actor_url': teacher['url'], 'actor_name': teacher['name']}
    if teacher_list and len(teacher_list) > 1:
        _LOGGER.error("该番号抓取到多个老师，无法判断小明想要哪个老师教学")
    if not teacher_list:
        _LOGGER.error("没有爬取到该番号的信息，请检查番号是否正确")
    return None


def grab_jav_bus_by_name(actor_name, jav_bus_cookie, ua, proxies):
    cookie_dict = str_cookies_to_dict(jav_bus_cookie)
    headers = {'cookie': jav_bus_cookie, 'Referer': "https://www.javbus.com", }
    if ua:
        headers['User-Agent'] = ua
    for host in jav_bus_urls:
        url = f"{host}/searchstar/{actor_name}"
        try:
            res = requests.get(url=url, proxies=proxies, headers=headers, cookies=cookie_dict)
            break
        except Exception as e:
            continue
    if not res:
        _LOGGER.error("爬虫出错，检查网络")
        return None
    soup = bs4.BeautifulSoup(res.text, 'html.parser')
    actors = soup.select('a.avatar-box')
    if len(actors) > 1:
        _LOGGER.info("搜索出了多个演员,请输入更为详细的演员艺名")
        return None
    if len(actors) < 1:
        _LOGGER.info("演员艺名错误")
        return None
    actor_url = actors[0].get('href')
    actor_name = actors[0].select('div.photo-frame>img')[0].get('title')
    return {'actor_url': actor_url, 'actor_name': actor_name}


def grab_actor(actor_url, jav_bus_cookie: str, ua, proxies, start_date):
    time.sleep(5)
    if 'exitmad' not in jav_bus_cookie:
        jav_bus_cookie = f"exitmad=all;{jav_bus_cookie}"
    else:
        jav_bus_cookie = jav_bus_cookie.replace('existmag=mag', 'existmag=all')
    cookie_dict = str_cookies_to_dict(jav_bus_cookie)
    headers = {'cookie': jav_bus_cookie, 'Referer': "https://www.javbus.com", }
    if ua:
        headers['User-Agent'] = ua
    star_codes = actor_url.split('/')
    star_code = star_codes[len(star_codes) - 1]
    for host in jav_bus_urls:
        url = f"{host}/star/{star_code}"
        try:
            res = requests.get(url=url, proxies=proxies, headers=headers, cookies=cookie_dict)
            break
        except Exception as e:
            continue
    if not res:
        _LOGGER.error("爬虫出错，检查网络")
        return None
    soup = bs4.BeautifulSoup(res.text, 'html.parser')
    movie_list = soup.select('a.movie-box')
    code_list = []
    for item in movie_list:
        date_list = item.select('date')
        code_list.append({'date': date_list[1].text, 'code': date_list[0].text})
    start_date_timestamp = int(datetime.datetime.strptime(start_date, "%Y-%m-%d").strftime('%Y%m%d'))
    filter_list = list(
        filter(
            lambda x: int(datetime.datetime.strptime(x['date'], "%Y-%m-%d").strftime('%Y%m%d')) >= start_date_timestamp
                      and 'VR' not in x['code'],
            code_list))
    _LOGGER.info("对超过时间限定和带有VR标记的番号进行筛选")
    finally_list = []
    for item in filter_list:
        time.sleep(5)
        teacher_list = get_teacher_list(item['code'], jav_bus_cookie, ua, proxies)
        teacher_num = None
        if teacher_list:
            teacher_num = len(teacher_list)
        if teacher_num and teacher_num < 4:
            finally_list.append(item)
        if teacher_num and teacher_num > 3:
            _LOGGER.info(f"{item['code']}检索到超过3名老师进行教学,小明应付不了")
        if not teacher_num:
            _LOGGER.info(f"{item['code']}没有检索到老师,可能爬虫出了问题")
    return finally_list


def get_teacher_list(code, jav_bus_cookie, ua, proxies):
    cookie_dict = str_cookies_to_dict(jav_bus_cookie)
    headers = {'cookie': jav_bus_cookie, 'Referer': "https://www.javbus.com", }
    if ua:
        headers['User-Agent'] = ua
    for host in jav_bus_urls:
        url = f"{host}/{code}"
        try:
            res = requests.get(url=url, proxies=proxies, headers=headers, cookies=cookie_dict)
            break
        except Exception as e:
            continue
    if not res:
        _LOGGER.error("爬虫出错，检查网络")
        return None
    soup = bs4.BeautifulSoup(res.text, 'html.parser')
    actor_list = soup.select('span.genre>a')
    if actor_list:
        teacher_list = []
        for actor in actor_list:
            name = actor.text
            url = actor.get('href')
            teacher_list.append({'name': name, 'url': url})
            return teacher_list
    return None


def grab_m_team(keyword):
    url = f'https://kp.m-team.cc/adult.php?incldead=1&spstate=0&inclbookmarked=0&search={keyword}&search_area=0&search_mode=0'
    m_team_cookies = get_m_team_cookie()
    user_agent = get_m_team_ua()
    cookie_str = get_m_team_cookie_str()
    headers = {'cookie': cookie_str, 'Referer': "https://kp.m-team.cc"}
    if user_agent:
        headers['User-Agent'] = user_agent
    res = requests.get(url, cookies=m_team_cookies, headers=headers)
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
        weight = get_weight(title, describe, int(seeders), size)
        torrent['weight'] = weight
        torrents.append(torrent)
    return torrents


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


def get_best_torrent(torrents):
    if torrents:
        sort_list = sorted(torrents, key=lambda torrent: torrent['weight'], reverse=True)
        torrent = sort_list[0]
        if torrent['weight'] < 0:
            return None
        return torrent
    return None


def download_torrent(code, download_url, torrent_folder):
    host = 'https://kp.m-team.cc/'
    cookies = get_m_team_cookie()
    res = requests.get(host + download_url, cookies=cookies)
    torrent_path = f'{torrent_folder}/{code}.torrent'

    with open(torrent_path, 'wb') as torrent:
        torrent.write(res.content)
        torrent.flush()
    return torrent_path


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


def get_m_team_ua():
    site_list = server.site.list()
    mteam_list = list(
        filter(lambda x: x.site_id == 'mteam', site_list))
    if len(mteam_list) > 0:
        mteam = mteam_list[0]
        user_agent = mteam.user_agent
        return user_agent
    return None


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
