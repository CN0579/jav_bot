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
