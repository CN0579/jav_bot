import os
import random
import shutil
import time

from mbot.openapi import mbot_api
import logging
from mbot.core.params import ArgSchema, ArgType
from mbot.core.plugins import plugin, PluginCommandContext, PluginCommandResponse
from .event import update_top_rank, download_by_codes
from .mdc import mdc_command
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


@plugin.command(name='mdc', title='一键刮削', desc='刮削目录为插件中配置的目录',
                icon='',
                run_in_background=True)
def mdc(
        ctx: PluginCommandContext,
        path: ArgSchema(ArgType.String, '刮削路径', '')):
    try:
        mdc_command(path)
    except Exception as e:
        _LOGGER.error(e, exc_info=True)
        return PluginCommandResponse(False, f'一键刮削成功')
    return PluginCommandResponse(True, f'一键刮削失败')


# def get_un_download_chapter():
#     chapters = list_un_download_chapter()
#     enum_data = [{'value': chapter['id'], 'name': chapter['chapter_code']} for chapter in chapters]
#     return enum_data
#
#
# @plugin.command(name='delete_wanted', title='删除想看的番号', desc='删除数据,不可恢复', icon='', run_in_background=True)
# def delete_wanted(
#         ctx: PluginCommandContext,
#         code_id_list: ArgSchema(ArgType.Enum, '选择删除的番号', '', enum_values=get_un_download_chapter,
#                                 multi_value=True)):
#     try:
#         if code_id_list:
#             code_id_str_list = [str(code_id) for code_id in code_id_list]
#             code_ids = ','.join(code_id_str_list)
#             delete_chapter(code_ids)
#             _LOGGER.info(f"删除ID为{code_ids}的想要番号成功")
#     except Exception as e:
#         _LOGGER.error(e, exc_info=True)
#         return PluginCommandResponse(False, f'删除成功')
#     return PluginCommandResponse(True, f'删除失败')
