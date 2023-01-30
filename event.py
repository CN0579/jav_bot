import os
import random
import shutil
import threading
import time
import typing

import requests
import bs4
from mbot.openapi import mbot_api
from mbot.core.plugins import *
from typing import Dict, Any
import logging
from .sql import *
from .scraper import *
from .download import *
from . import libmdc_ng

_LOGGER = logging.getLogger(__name__)
server = mbot_api

path = ''
proxies = {
    'http': '',
    'https': '',
}
torrent_folder = '/data/plugins/jav_bot_torrents'
jav_cookie = ''
ua = ''

category = None

message_to_uid: typing.List[int] = []
client_name = ''
need_mdc = False
pic_url = 'https://api.r10086.com/img-api.php?type=%E6%9E%81%E5%93%81%E7%BE%8E%E5%A5%B3%E5%9B%BE%E7%89%87'


def init_config(config):
    global path, proxies, torrent_folder, jav_cookie, ua, category, \
        message_to_uid, client_name, need_mdc, pic_url
    if config.get('path'):
        path = config.get('path')
    if config.get('proxy'):
        proxies = {
            'http': config.get('proxy'),
            'https': config.get('proxy')
        }
    if config.get('jav_cookie'):
        jav_cookie = config.get('jav_cookie')
    if config.get('ua'):
        ua = config.get('ua')
    if config.get('category'):
        category = config.get('category')
    if config.get('uid'):
        message_to_uid = config.get('uid')
    if config.get('client_name'):
        client_name = config.get('client_name')
    need_mdc = config.get('need_mdc')
    if config.get('pic_url'):
        pic_url = config.get('pic_url')


@plugin.after_setup
def after_setup(plugin_meta: PluginMeta, config: Dict[str, Any]):
    init_config(config)
    create_database()
    if not os.path.exists(torrent_folder):
        os.mkdir(torrent_folder)


@plugin.config_changed
def config_changed(config: Dict[str, Any]):
    init_config(config)


@plugin.task('task', '定时任务', cron_expression='0 22 * * *')
def task():
    time.sleep(random.randint(1, 3600))
    update_top_rank()
    

def wait_all_torrent_completed(name, sleep_second):
    downloading_torrents = list_downloading_torrents(client_name=client_name)
    filter_dl_torrents = list(filter(lambda x: x.save_path.rstrip('/') == path.rstrip('/'), downloading_torrents))
    if len(filter_dl_torrents) > 0:
        time.sleep(sleep_second)
        wait_all_torrent_completed(name, sleep_second)
    else:
        _LOGGER.info(f"线程{name}:所有种子下载完成，开始执行MDC")
        mdc()


def mdc():
    _LOGGER.info("开始执行MDC")
    host = 'http://127.0.0.1'
    port = server.config.web.port
    url = f'{host}:{port}/api/plugins/mdc/start'
    res = requests.post(url)
    _LOGGER.info(res)


def collect_videos(path):
    videos = []
    if os.path.isdir(path):
        for file in os.listdir(path):
            videos.extend(collect_videos(os.path.join(path, file)))
        return videos
    elif os.path.splitext(path)[1].lower() in [
        ".mp4",
        ".avi",
        ".rmvb",
        ".wmv",
        ".mov",
        ".mkv",
        ".webm",
        ".iso",
        ".mpg",
        ".m4v",
    ]:
        return [path]
    else:
        return []


def filter_no_hard_link_path(paths):
    filter_list = []
    for path in paths:
        if os.stat(path).st_nlink < 2:
            filter_list.append(path)
    return filter_list

def mdc_a_jiang():
    _LOGGER.info("开始执行Ajiang MDC")
    global path
    paths = collect_videos(path)
    filter_paths = filter_no_hard_link_path(paths)
    _LOGGER.info(f"需要整理的影片:{[p for p in filter_paths]}")
    for filter_path in filter_paths:
        libmdc_ng.main(filter_path, '/video/links/学习资料/整理')
    _LOGGER.info("整理完成")

# 指令1
# 更新榜单,新晋番号将进入想看列表
# 查询想看列表未下载的资源，并从馒头爬取资源进行下载
def update_top_rank():
    new_code_list = save_new_code()
    if new_code_list:
        push_new_code_msg(new_code_list)
    download_code_list = fetch_un_download_code()
    if download_code_list:
        push_new_download_msg(download_code_list)
    _LOGGER.error("更新榜单完成")
    if need_mdc:
        _LOGGER.info("等待所有种子下载完成")
        t = threading.Thread(target=wait_all_torrent_completed, args=('jav_bot', 60,))
        t.start()
        return

 
# 指令2
# 将指定的番号加入想看列表
# 从馒头爬取资源并下载
def download_by_codes(codes: str):
    code_list = codes.split(',')
    for code in code_list:
        if not code:
            continue
        res = download_by_code(code)
        _LOGGER.info(res)
        _LOGGER.info("等待10-20S继续操作")
        time.sleep(random.randint(10, 20))
    if need_mdc:
        _LOGGER.info("等待所有种子下载完成")
        t = threading.Thread(target=wait_all_torrent_completed, args=('jav_bot', 30,))
        t.start()
        return


# 将输入不规范的番号规范化返回
def get_true_code(input_code: str):
    code_list = input_code.split('-')
    code = ''.join(code_list)
    length = len(code)
    index = length - 1
    num = ''
    all_number = '0123456789'
    while index > -1:
        s = code[index]
        if s not in all_number:
            break
        num = s + num
        index = index - 1
    prefix = code[0:index + 1]
    return (prefix + '-' + num).upper()


#
def download_by_code(code: str):
    code = get_true_code(code)
    chapter = get_chapter(code)
    if not chapter:
        chapter = {
            'code': code,
            'overview': '手动添加番号,暂时无法获取简介',
            'img': ''
        }
        save_chapter(chapter)
        push_new_code_msg([code])
    chapter = get_chapter(code)
    if chapter['status'] == 1:
        return f'你已经下载过番号{code}'

    torrents = grab_m_team(code)
    if torrents:
        torrent = get_best_torrent(torrents)
        torrent_path = download_torrent(code, torrent['download_url'], torrent_folder)
        res = download(torrent_path, save_path=path, category=category, client_name=client_name)
        if res:
            chapter['size'] = torrent['size']
            chapter['download_url'] = torrent['download_url']
            chapter['download_path'] = path
            update_chapter(chapter)
            push_new_download_msg([code])
            return f'已开始下载番号{code}'
        else:
            return '添加种子失败'
    else:
        return f'没用找到该番号{code}的种子,已保存到想看的科目列表'


# 保存新晋番号到想看列表
def save_new_code():
    av_list = grab_jav(1, jav_cookie, ua, proxies)
    if not av_list:
        _LOGGER.error('爬取jav失败')
        return
    new_chapter = []
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
            new_chapter.append(code)
    return new_chapter


def push_msg(title, content):
    for uid in message_to_uid:
        server.notify.send_message_by_tmpl('{{title}}', '{{a}}', {
            'title': title,
            'a': content,
            'link_url': '',
            'pic_url': pic_url
        }, to_uid=uid)


# 有新的科目进入20大榜单
def push_new_code_msg(code_list):
    title = '有新的学习资料进入想看列表'
    content = ','.join(code_list)
    push_msg(title, content)


# 想要的科目开始下载
def push_new_download_msg(code_list):
    title = '有新的学习资料开始下载'
    content = ','.join(code_list)
    push_msg(title, content)


# 获取未下载的番号
# 从馒头爬取最佳资源下载
def fetch_un_download_code():
    cookies = get_m_team_cookie()
    if not cookies:
        _LOGGER.error('尚未配置馒头站点')
        return
    chapters = list_un_download_chapter()
    _LOGGER.info(f"尚未下载的科目:{[chapter['chapter_code'] for chapter in chapters]}")
    download_chapter = []
    for chapter in chapters:
        code = chapter['chapter_code']
        torrents = grab_m_team(code)
        if torrents:
            torrent = get_best_torrent(torrents)
            if torrent:
                torrent_path = download_torrent(code, torrent['download_url'], torrent_folder)
                res = download(torrent_path, save_path=path, category=category, client_name=client_name)
                if res:
                    chapter['size'] = torrent['size']
                    chapter['download_url'] = torrent['download_url']
                    chapter['download_path'] = path
                    update_chapter(chapter)
                    download_chapter.append(code)
                else:
                    _LOGGER.error('添加种子失败')
            else:
                _LOGGER.info("没有正在做中的种子")
        else:
            _LOGGER.info(f"{code}:尚无资源")
        _LOGGER.info("等待10-20S继续操作")
        time.sleep(random.randint(10, 20))
    return download_chapter
