import configparser
import datetime
import os
import logging
import stat
import sys

from .tools import *

_LOGGER = logging.getLogger(__name__)
config_path = f'{os.path.abspath(os.path.dirname(__file__))}/config.ini'


def get_mdc():
    if 'plugins.mdc_mbot_plugin' not in sys.modules:
        _LOGGER.error("mdc模块尚未安装，无法进行刮削整理")
        return None
    from plugins.mdc_mbot_plugin import mdc_main
    _LOGGER.error("mdc模块已安装")
    return mdc_main


def mdc_aj(path):
    mdc = get_mdc()
    if mdc:
        _LOGGER.info("开始执行MDC")
        videos = collect_videos(path)
        adult_video = get_max_size_video(videos)
        try:
            mdc(adult_video, config_path)
            _LOGGER.error(f"{adult_video}整理成功")
        except Exception as e:
            conf = configparser.ConfigParser()
            conf.read(config_path)
            fail_folder = conf.get('common', 'fail_folder')
            write_fail_log(fail_videos=[adult_video], fail_folder=fail_folder)
            _LOGGER.error(f"{adult_video}整理失败")


def is_hardlink(src, dst):
    s1 = os.stat(src)
    s2 = os.stat(dst)
    return (s1[stat.ST_INO], s1[stat.ST_DEV]) == (s2[stat.ST_INO], s2[stat.ST_DEV])


def find_hard_link(src, videos):
    for video in videos:
        if is_hardlink(src, video):
            return True
    return False


def mdc_command(path):
    conf = configparser.ConfigParser()
    conf.read(config_path)
    target_folder = conf.get('common', 'target_folder')
    fail_folder = conf.get('common', 'fail_folder')
    if not target_folder:
        _LOGGER.error("没有设置刮削成功目录")
        return
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)
    mdc = get_mdc()
    if mdc:
        videos = collect_videos(path)
        hard_link_videos = collect_videos(target_folder)
        fail_videos = []
        for video in videos:
            if find_hard_link(video, hard_link_videos):
                _LOGGER.error(f"文件{video},已存在整理文件，跳过刮削")
                continue
            if os.path.getsize(video) < 200 * 1024 * 1000:
                _LOGGER.error(f"文件体积小于200M,跳过刮削")
                continue
            try:
                mdc(video, config_path)
            except Exception as e:
                _LOGGER.error(f"肥肠抱歉,文件{video}刮削失败")
                fail_videos.append(video)
                continue
        write_fail_log(fail_videos, fail_folder)


def write_fail_log(fail_videos, fail_folder):
    if fail_folder:
        _LOGGER.info("开始写入刮削失败的文件")
        if not os.path.exists(fail_folder):
            os.makedirs(fail_folder)
        now_str = datetime.datetime.now().strftime('%Y年%m月%d日%H时%M分%S秒')
        if not os.path.exists('fail'):
            os.makedirs('fail')
        note = open(f'{fail_folder}/{now_str}.txt', mode='a')
        for video in fail_videos:
            note.writelines(f"{video}\n")
        note.close()
