import gc
import os
import random
import shutil
import time

from mbot.openapi import mbot_api
import logging
from mbot.core.params import ArgSchema, ArgType
from mbot.core.plugins import plugin, PluginCommandContext, PluginCommandResponse
from .event import update_top_rank, download_by_codes, add_actor, upgrade_jav_bot
from .mdc import mdc_command
from .sql import *

server = mbot_api
_LOGGER = logging.getLogger(__name__)
namespace = os.path.split(os.path.abspath(os.path.dirname(__file__)))[1]
file_name = os.path.split(__file__)[1]
file_name = file_name[0:len(file_name) - 3]
module_name = f"{namespace}.{file_name}"


def get_base_commands():
    commands = [
        {'name': '更新TOP20榜单', 'value': 'update_rank'},
        {'name': '插件升级', 'value': 'upgrade_plugin'},
    ]
    return commands


@plugin.command(name='base_command', title='学习工具:更新', desc='', icon='', run_in_background=True)
def base_command(ctx: PluginCommandContext,
                 command: ArgSchema(ArgType.Enum, '选择操作', '', enum_values=get_base_commands, multi_value=False)):
    if command == 'update_rank':
        update_top_rank()
    if command == 'upgrade_plugin':
        upgrade_jav_bot()
    _LOGGER.info("更新完成")

@plugin.command(name='subscribe_command', title='学习工具:订阅', desc='', icon='', run_in_background=True)
def subscribe_command(
        ctx: PluginCommandContext,
        codes: ArgSchema(ArgType.String, '番号订阅', '输入番号,多个番号用英文逗号隔开'),
        keyword: ArgSchema(ArgType.String, '教师订阅-关键字', '输入教师姓名或是单人授课科目名'),
        start_date: ArgSchema(ArgType.String, '教师订阅-时间限制', '日期格式务必准确,例如:2023-01-01')
):
    if codes:
        download_by_codes(codes)
    if keyword and start_date:
        try:
            datetime.datetime.strptime(start_date, '%Y-%d-%m')
        except Exception as e:
            _LOGGER.error("日期格式错误")
            return
        add_actor(keyword, start_date)
    _LOGGER.info("订阅完成")
    return PluginCommandResponse(True, '')


@plugin.command(name='mdc', title='一键刮削', desc='刮削目录为插件中配置的目录',
                icon='',
                run_in_background=True)
def mdc(
        ctx: PluginCommandContext,
        path: ArgSchema(ArgType.String, '刮削路径', '')):
    mdc_command(path)
    _LOGGER.info("一键刮削完成")
    return PluginCommandResponse(True, '')


def get_un_download_chapter():
    chapters = list_un_download_chapter()
    enum_data = [{'value': chapter['id'], 'name': chapter['chapter_code']} for chapter in chapters]
    return enum_data


def get_actors():
    actor_list = list_actor()
    enum_data = [{'value': actor['id'], 'name': f"{actor['actor_name']}-{actor['start_date']}"} for actor in actor_list]
    return enum_data


@plugin.command(name='delete_wanted', title='学习工具:数据', desc='', icon='', run_in_background=True)
def delete_wanted(
        ctx: PluginCommandContext,
        code_list: ArgSchema(ArgType.Enum, '选择想要删除的科目', '', enum_values=get_un_download_chapter, multi_value=True),
        actor_list: ArgSchema(ArgType.Enum, '选择想要删除的教师', '', enum_values=get_actors, multi_value=True)

):
    if code_list:
        code_id_str_list = [str(code_id) for code_id in code_list]
        code_ids = ','.join(code_id_str_list)
        delete_chapter(code_ids)
        _LOGGER.info(f"删除ID为{code_ids}的科目成功")
    if actor_list:
        actor_id_str_list = [str(actor_id) for actor_id in actor_list]
        actor_ids = ','.join(actor_id_str_list)
        delete_actor(actor_ids)
        _LOGGER.info(f"删除ID为{actor_ids}的老师成功")
    return PluginCommandResponse(True, '')
