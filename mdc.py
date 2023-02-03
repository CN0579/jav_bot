import os
import logging
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
        mdc(adult_video, config_path)
        _LOGGER.info("整理完成")


def is_hardlink(filepath):
    sfs = os.stat(filepath)
    return sfs.st_nlink > 1


def mdc_command(path):
    mdc = get_mdc()
    if mdc:
        videos = collect_videos(path)
        for video in videos:
            if is_hardlink(video):
                continue
            if os.path.getsize(video) < 1024 * 1000:
                continue
            mdc(video, config_path)
