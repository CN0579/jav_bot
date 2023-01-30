import logging
import os
import os.path
from typing import Dict

from mbot.core.event.models import EventType
from mbot.core.plugins import plugin
from mbot.core.plugins import PluginContext

from .client import *

from . import libmdc_ng

_LOGGER = logging.getLogger(__name__)
# formatter = logging.Formatter(
#     "%(levelname)s %(name)s %(asctime)-15s %(filename)s:%(lineno)d %(message)s"
# )
# handler = logging.StreamHandler()
# handler.setFormatter(formatter)
# _LOGGER.addHandler(handler)


@plugin.on_event(bind_event=[EventType.DownloadCompleted], order=1)
def on_event(ctx: PluginContext, event_type: str, data: Dict):
    """
    触发绑定的事件后调用此函数
    函数接收参数固定。第一个为插件上下文信息，第二个事件类型，第三个事件携带的数据
    """

    _LOGGER.info("MDC 事件测试: EventType.DownloadCompleted")
    _LOGGER.info(event_type)
    _LOGGER.info(data)


# {'name': '三体.ThreeBody.S01.2023.2160p.V2.WEB-DL.H265.AAC-HHWEB', 'hash': '96773744314c9a487462a86b9d04dbb90ca7ce14', 'save_path': '/nas/downloads/tv/', 'content_path': '/nas/downloads/tv/三体.ThreeBody.S01.2023.2160p.V2.WEB-DL.H265.AAC-HHWEB/ThreeBody.S01E16.2023.2160p.V2.WEB-DL.H265.AAC-HHWEB.mp4', 'progress': 100, 'size': 1081936959, 'size_str': '1.01 GB', 'dlspeed': 0, 'dlspeed_str': '0', 'upspeed': 0, 'upspeed_str': '0', 'uploaded': 3172779138, 'uploaded_str': '2.95 GB', 'seeding_time': 7512, 'downloaded': 1092912248, 'downloaded_str': '1.02 GB', 'ratio': 2.903050216342712, 'tracker': 'https://hhanclub.top/announce.php?authkey=15854|13946|2XE18z'}

download_dir = "/misc/downloads"
target_dir = "/misc/adult"


@plugin.task("task", "定时任务", cron_expression="* * * * *")
def task():
    _LOGGER.info("MDC 定时任务启动")
    for torrent in recent_completed_torrents(""):
        path = torrent.content_path
        if not path.startswith(download_dir):
            continue
        _LOGGER.info("检测到新下载种子")
        _LOGGER.info("开始处理种子路径: %s", path)
        videos = collect_videos(path)
        if len(videos) > 5:
            _LOGGER.info("视频文件数量多于5个，不处理")
            continue

        for video in videos:
            _LOGGER.info("MDC 开始处理视频文件: %s", video)
            try:
                libmdc_ng.main(video, target_dir)
            except Exception as e:
                _LOGGER.error("处理视频文件出错: %s", video)
                _LOGGER.error(e)
                continue
            _LOGGER.info("处理视频文件完成: %s", video)


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
