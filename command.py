import os
import random
import shutil
import time

from mbot.openapi import mbot_api
import logging
from mbot.core.params import ArgSchema, ArgType
from mbot.core.plugins import plugin, PluginCommandContext, PluginCommandResponse
from .event import command, download_by_code, download_completed

server = mbot_api
_LOGGER = logging.getLogger(__name__)


@plugin.command(name='update_rate', title='更新并下载', desc='更新学习资料榜单数据，并提交下载,请注意是否已进行过配置',
                icon='',
                run_in_background=True)
def update_rate(ctx: PluginCommandContext):
    try:
        command()
    except Exception as e:
        _LOGGER.error(e, exc_info=True)
        return PluginCommandResponse(False, f'创建数据源失败')
    return PluginCommandResponse(True, f'创建数据源成功')


@plugin.command(name='download', title='下载指定科目', desc='下载指定科目,如果科目不存在，则会进入想看科目列表', icon='',
                run_in_background=True)
def download(
        ctx: PluginCommandContext,
        codes: ArgSchema(ArgType.String, '科目名称', '填入想要学习的科目,多个科目用英文逗号隔开')):
    try:
        code_list = codes.split(',')
        for code in code_list:
            res = download_by_code(code)
            _LOGGER.info(res)
            time.sleep(random.randint(10, 20))
    except Exception as e:
        _LOGGER.error(e, exc_info=True)
        return PluginCommandResponse(False, f'获取科目失败')
    return PluginCommandResponse(True, f'获取科目成功')


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
        download_completed()
    except Exception as e:
        _LOGGER.error(e, exc_info=True)
        return PluginCommandResponse(False, f'创建数据源失败')
    return PluginCommandResponse(True, f'创建数据源成功')


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
