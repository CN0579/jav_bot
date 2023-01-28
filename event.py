import os
import random
import shutil
import time
import typing

import requests
import bs4
from mbot.openapi import mbot_api
from mbot.core.plugins import *
from typing import Dict, Any
import logging
from .sql import *
from .qbittorrent import *
from .scraper import *

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
qb_name = ''
hard_link_dir = ''
need_hard_link = False
need_mdc = False
mdc_exclude_dir = ''
pic_url = 'https://api.r10086.com/img-api.php?type=%E6%9E%81%E5%93%81%E7%BE%8E%E5%A5%B3%E5%9B%BE%E7%89%87'


@plugin.after_setup
def after_setup(plugin_meta: PluginMeta, config: Dict[str, Any]):
    global path, proxies, torrent_folder, jav_cookie, ua, category, \
        message_to_uid, qb_name, hard_link_dir, need_hard_link, need_mdc, mdc_exclude_dir, pic_url
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
    if config.get('qb_name'):
        qb_name = config.get('qb_name')
    if config.get('hard_link_dir'):
        hard_link_dir = config.get('hard_link_dir')
    need_hard_link = config.get('need_hard_link')
    need_mdc = config.get('need_mdc')
    if config.get('mdc_exclude_dir'):
        mdc_exclude_dir = config.get('mdc_exclude_dir')
    if config.get('pic_url'):
        pic_url = config.get('pic_url')
    create_database()
    if not os.path.exists(torrent_folder):
        os.mkdir(torrent_folder)


@plugin.config_changed
def config_changed(config: Dict[str, Any]):
    global path, proxies, torrent_folder, jav_cookie, ua, category, \
        message_to_uid, qb_name, hard_link_dir, need_hard_link, need_mdc, mdc_exclude_dir, pic_url
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
    if config.get('qb_name'):
        qb_name = config.get('qb_name')
    if config.get('hard_link_dir'):
        hard_link_dir = config.get('hard_link_dir')
    need_hard_link = config.get('need_hard_link')
    need_mdc = config.get('need_mdc')
    if config.get('mdc_exclude_dir'):
        mdc_exclude_dir = config.get('mdc_exclude_dir')
    if config.get('pic_url'):
        pic_url = config.get('pic_url')


@plugin.task('task', '定时任务', cron_expression='0 22 * * *')
def task():
    time.sleep(random.randint(1, 3600))
    update_top_rank()


# 指令1
# 更新榜单,新晋番号将进入想看列表
# 查询想看列表未下载的资源，并从馒头爬取资源进行下载
def update_top_rank():
    if login_qb(qb_name):
        new_code_list = save_new_code()
        if new_code_list:
            push_new_code_msg(new_code_list)
        download_code_list = fetch_un_download_code()
        if download_code_list:
            push_new_download_msg(download_code_list)
        _LOGGER.error("精品科目,执行结束")
    else:
        _LOGGER.error('QB登录失败')


# 指令2
# 将指定的番号加入想看列表
# 从馒头爬取资源并下载
def download_by_codes(codes: str):
    if login_qb(qb_name):
        code_list = codes.split(',')
        for code in code_list:
            if not code:
                continue
            res = download_by_code(code)
            _LOGGER.info(res)
            _LOGGER.info("等待10-20S继续操作")
            time.sleep(random.randint(10, 20))
    else:
        _LOGGER.error("qb登录失败")


# 指令3
# 将下载完成的种子硬链
# 通过MDC整理学习资料
def hard_link_and_mdc():
    if login_qb():
        mdc_path = path
        if need_hard_link:
            mdc_path = hard_link_dir
            complete_torrent_hard_link()
        if need_mdc:
            mdc(mdc_path)
    else:
        _LOGGER.error('QB登录失败')


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
        res = download(torrent_path, save_path=path, category=category)
        if res == 'Ok.':
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


def mdc(dir):
    exclude_dir = mdc_exclude_dir
    _LOGGER.info(f"即将开始整理目录{dir}的学习资料，排除目录{exclude_dir}")


# 将下载完成的种子，硬链到指定目录
def complete_torrent_hard_link():
    torrent_list = list_completed_unlink_torrents()
    if torrent_list:
        for torrent in torrent_list:
            content_path = torrent.get('content_path')
            torrent_hash = torrent.get('hash')
            hard_link(content_path)
            qb.torrents_remove_tags('unlink', torrent_hashes=[torrent_hash])
            qb.torrents_add_tags(tags='linked', torrent_hashes=[torrent_hash])


# 硬链到配置的目录下
def hard_link(file_content):
    global hard_link_dir
    hard_link_dir = hard_link_dir.strip()
    hard_link_dir = hard_link_dir.rstrip("\\")
    if not os.path.exists(hard_link_dir):
        os.makedirs(hard_link_dir)
    basename = os.path.basename(file_content)
    hard_link_path = f"{hard_link_dir.rstrip('/')}/{basename}"
    if os.path.isdir(file_content):
        shutil.copytree(file_content, hard_link_path, copy_function=os.link)
    if os.path.isfile(file_content):
        os.link(file_content, hard_link_path)


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
    title = '有新的科目进入想看列表'
    content = ','.join(code_list)
    push_msg(title, content)


# 想要的科目开始下载
def push_new_download_msg(code_list):
    title = '你想看的科目上架了,正在下载'
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
                res = download(torrent_path, save_path=path, category=category)
                if res == 'Ok.':
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
