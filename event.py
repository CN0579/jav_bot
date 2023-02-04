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
from .mdc import *
from .tools import *
import configparser
from .upgrade import *

_LOGGER = logging.getLogger(__name__)
server = mbot_api

path = ''
proxies = {
    'http': '',
    'https': '',
}
plugin_folder = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
torrent_folder = f'{plugin_folder}/jav_bot_torrents'
jav_cookie = ''
jav_bus_cookie = ''
ua = ''

category = None

message_to_uid: typing.List[int] = []
client_name = ''
need_mdc = False
hard_link_dir = ''
pic_url = 'https://api.r10086.com/img-api.php?type=%E6%9E%81%E5%93%81%E7%BE%8E%E5%A5%B3%E5%9B%BE%E7%89%87'
fail_folder = ''


def init_config(config):
    global path, proxies, torrent_folder, jav_cookie, ua, category, \
        message_to_uid, client_name, need_mdc, pic_url, hard_link_dir, jav_bus_cookie, fail_folder
    if config.get('path'):
        path = config.get('path')
    if config.get('proxy'):
        proxies = {
            'http': config.get('proxy'),
            'https': config.get('proxy')
        }
    if config.get('jav_cookie'):
        jav_cookie = config.get('jav_cookie')
    if config.get('jav_bus_cookie'):
        jav_bus_cookie = config.get('jav_bus_cookie')
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
    if config.get('hard_link_dir'):
        hard_link_dir = config.get('hard_link_dir')
    if config.get('fail_folder'):
        fail_folder = config.get('fail_folder')
    create_config_ini(config.get('proxy'), hard_link_dir, fail_folder)


def create_config_ini(proxy, target_folder, failed_folder):
    conf = configparser.ConfigParser()
    conf['common'] = {'target_folder': target_folder, 'fail_folder': failed_folder}
    conf['proxy'] = {'proxy': proxy}
    config_ini_path = f'{os.path.abspath(os.path.dirname(__file__))}/config.ini'
    if os.path.exists(config_ini_path):
        os.remove(config_ini_path)
    with open(config_ini_path, 'w') as cfg:
        conf.write(cfg)


@plugin.after_setup
def after_setup(plugin_meta: PluginMeta, config: Dict[str, Any]):
    init_config(config)
    create_database()
    create_download_record_table()
    create_actor_table()
    if not os.path.exists(torrent_folder):
        os.mkdir(torrent_folder)
    after_rebot()


@plugin.config_changed
def config_changed(config: Dict[str, Any]):
    init_config(config)


@plugin.task('task', '定时任务', cron_expression='0 22 * * *')
def task():
    time.sleep(random.randint(1, 3600))
    update_top_rank()
    subscribe_by_actor()


def add_actor(keyword: str, start_date):
    if len(keyword) == len(keyword.encode()):
        true_code = get_true_code(keyword)
        actor_grab = grab_jav_bus_by_code(true_code, jav_bus_cookie, ua, proxies)
    else:
        actor_grab = grab_jav_bus_by_name(keyword, jav_bus_cookie, ua, proxies)
    flag = False
    if actor_grab:
        actor_url = actor_grab['actor_url']
        actor_name = actor_grab['actor_name']
        actor = get_actor_by_url(actor_url)
        if actor:
            flag = False
            update_actor(actor['id'], start_date)
            _LOGGER.info(f"{actor_name}已存在订阅的演员列表中")
        else:
            flag = True
            actor = {
                'actor_name': actor_name,
                'actor_url': actor_url,
                'start_date': start_date
            }
            save_actor(actor)
            _LOGGER.info(f"{actor_name}订阅完成")
        code_list = grab_actor(actor_url, jav_bus_cookie, ua, proxies, start_date)
        if code_list:
            codes = ','.join([code['code'] for code in code_list])
            download_by_codes(codes=codes)
    return flag


def subscribe_by_actor():
    actor_list = list_actor()
    for actor in actor_list:
        actor_url = actor['actor_url']
        start_date = actor['start_date']
        code_list = grab_actor(actor_url, jav_bus_cookie, ua, proxies, start_date)
        codes = ','.join(code_list)
        download_by_codes(codes=codes)


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


# 指令2
# 将指定的番号加入想看列表
# 从馒头爬取资源并下载
def download_by_codes(codes: str):
    code_list = codes.split(',')
    for index, code in enumerate(code_list):
        if not code:
            continue
        res = download_by_code(code)
        _LOGGER.info(res)
        if index < len(code_list) - 1:
            _LOGGER.info("等待10-20S继续操作")
            time.sleep(random.randint(10, 20))


def upgrade_jav_bot():
    upgrade_project(proxies=proxies, retry_time=1)


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
        if torrent:
            torrent_path = download_torrent(code, torrent['download_url'], torrent_folder)
            res = download(torrent_path, save_path=path, category=category, client_name=client_name)
            if res:
                chapter['size'] = torrent['size']
                chapter['download_url'] = torrent['download_url']
                chapter['download_path'] = path
                update_chapter(chapter)
                push_new_download_msg([code])
                monitor_download_progress(torrent_path, 1)
                return f'已开始下载番号{code}'
            else:
                return '添加种子失败'
        else:
            return '没有有效的种子'
    else:
        return f'没有找到该番号{code}的种子,已保存到想看的科目列表'


def after_rebot():
    _LOGGER.info("重启服务器之后,将还在下载跟下载完成没有刮削的纳入监听")
    download_records = list_downloading_record()
    for record in download_records:
        torrent_file_hash = record['torrent_hash']
        t = threading.Thread(target=wait_torrent_downloaded, args=(torrent_file_hash,))
        t.start()


def monitor_download_progress(torrent_path, retry_time):
    if need_mdc:
        if retry_time > 3:
            _LOGGER.info(f"重试三次没有取到种子,放弃监听{torrent_path}的种子")
            return
        torrent = get_torrent_by_torrent_path(client_name=client_name, torrent_file=torrent_path)
        _LOGGER.info(f"开启监控种子:{torrent.name}的下载进度")
        if torrent:
            save_download_record(torrent)
            torrent_file_hash = torrent.hash
            t = threading.Thread(target=wait_torrent_downloaded, args=(torrent_file_hash,))
            t.start()
        else:
            _LOGGER.info(f"通过hash没取到种子,等待5S重试")
            time.sleep(5)
            monitor_download_progress(torrent_path, retry_time + 1)


def wait_torrent_downloaded(torrent_file_hash: str):
    torrent = get_by_hash(client_name=client_name, torrent_file_hash=torrent_file_hash)
    if not torrent:
        _LOGGER.info(f"种子名:{torrent.name}可能已被移出下载器,监听程序结束")
        return
    progress = torrent.progress
    _LOGGER.info(f"种子名:{torrent.name}当前的下载进度:{progress}%")
    if int(progress == 100):
        update_download_record(torrent_file_hash)
        push_downloaded(torrent.name)
        _LOGGER.info(f"种子名:{torrent.name}下载完成,开始执行MDC")
        mdc_aj(torrent.content_path)
    else:
        time.sleep(45)
        wait_torrent_downloaded(torrent_file_hash)


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
    for index, chapter in enumerate(chapters):
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
                    monitor_download_progress(torrent_path, 1)
                else:
                    _LOGGER.error('添加种子失败')
            else:
                _LOGGER.info("没有有效的种子")
        else:
            _LOGGER.info(f"{code}:尚无资源")
        if index < len(chapters) - 1:
            _LOGGER.info("等待10-20S继续操作")
            time.sleep(random.randint(10, 20))
    return download_chapter


# 推送相关代码
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


def push_downloaded(torrent_name):
    title = '有新的学习资料下载完成'
    push_msg(title, torrent_name)
