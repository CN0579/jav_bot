import os
import random
import shutil
import time

from mbot.openapi import mbot_api
import logging
from mbot.core.params import ArgSchema, ArgType
from mbot.core.plugins import plugin, PluginCommandContext, PluginCommandResponse
from .event import update_top_rank, download_by_codes
from .sql import *

server = mbot_api
_LOGGER = logging.getLogger(__name__)


@plugin.command(name='update_rate', title='一键添加新晋番号',
                        desc='新晋番号将进入想看列表,若存在资源会立刻进行下载',
                        icon='',
                        run_in_background=True)
def update_rate(ctx: PluginCommandContext):
    try:
        update_top_rank()
    except Exception as e:
        _LOGGER.error(e, exc_info=True)
        return PluginCommandResponse(False, f'创建数据源失败')
    return PluginCommandResponse(True, f'创建数据源成功')


@plugin.command(name='download', title='下载指定番号', desc='下载指定番号,若资源不存在，将会进入想看列表',
                        icon='',
                        run_in_background=True)
def download(
        ctx: PluginCommandContext,
        codes: ArgSchema(ArgType.String, '番号代码', '填入想要学习的番号,多个番号用英文逗号隔开')):
    try:
        download_by_codes(codes)
    except Exception as e:
        _LOGGER.error(e, exc_info=True)
        return PluginCommandResponse(False, f'下载指定番号失败')
    return PluginCommandResponse(True, f'下载指定番号成功')





