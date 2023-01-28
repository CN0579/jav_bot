import os
import random
import shutil
import time

from mbot.openapi import mbot_api
import logging
from mbot.core.params import ArgSchema, ArgType
from mbot.core.plugins import plugin, PluginCommandContext, PluginCommandResponse
from .event import update_top_rank, download_by_codes, hard_link_and_mdc
from .sql import *

server = mbot_api
_LOGGER = logging.getLogger(__name__)


@plugin.command(name='update_rate', title='添加新晋番号',
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


@plugin.command(name='hard_link', title='硬链', desc='硬链工具', icon='',
                        run_in_background=True)
def hard_link(
        ctx: PluginCommandContext,
        content_path: ArgSchema(ArgType.String, '源文件/目录路径', ''),
        hard_link_dir: ArgSchema(ArgType.String, '硬链接目录', ''),
        content_rename: ArgSchema(ArgType.String, '文件或目录重命名', '传空则默认源文件/目录名称')):
    hard_link_tool(content_path, hard_link_dir, content_rename)
    return PluginCommandResponse(True, f'硬链完成')


@plugin.command(name='hard_link_mdc', title='硬链并整理', desc='硬链并整理', icon='',
                        run_in_background=True)
def hard_link_mdc(ctx: PluginCommandContext):
    try:
        hard_link_and_mdc()
        _LOGGER.info("硬链整理完成")
    except Exception as e:
        _LOGGER.error(e, exc_info=True)

        return PluginCommandResponse(False, f'硬链整理失败')
    return PluginCommandResponse(True, f'硬链整理成功')


def hard_link_tool(content_path, hard_link_dir, content_rename):
    hard_link_dir = hard_link_dir.strip()
    hard_link_dir = hard_link_dir.rstrip("\\")
    if not os.path.exists(hard_link_dir):
        os.makedirs(hard_link_dir)
    basename = os.path.basename(content_path)
    if content_rename:
        basename = content_rename
    hard_link_path = f"{hard_link_dir.rstrip('/')}/{basename}"
    if os.path.isdir(content_path):
        shutil.copytree(content_path, hard_link_path, copy_function=os.link)
    if os.path.isfile(content_path):
        os.link(content_path, hard_link_path)
