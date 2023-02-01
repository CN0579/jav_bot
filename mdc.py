import requests
from mbot.openapi import mbot_api
import logging
from .tools import *
from . import libmdc_ng

_LOGGER = logging.getLogger(__name__)


def mdc_sks():
    _LOGGER.info("开始执行MDC_sks")
    host = 'http://127.0.0.1'
    port = mbot_api.config.web.port
    url = f'{host}:{port}/api/plugins/mdc/start'
    res = requests.post(url)
    _LOGGER.info(res)


def mdc_aj(path):
    _LOGGER.info("开始执行MDC_aj")
    videos = collect_videos(path)
    adult_video = get_max_size_video(videos)
    libmdc_ng.main(adult_video, '/data/plugins/jav_bot/config.ini')
    _LOGGER.info("整理完成")


def is_hardlink(filepath):
    sfs = os.stat(filepath)
    return sfs.st_nlink > 1


def mdc_command(path):
    videos = collect_videos(path)
    for video in videos:
        if is_hardlink(video):
            continue
        if os.path.getsize(video) < 1024 * 1000:
            continue
        libmdc_ng.main(video, '/data/plugins/jav_bot/config.ini')
