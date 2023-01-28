import random
import time

from mbot.openapi import mbot_api
import logging
from mbot.core.params import ArgSchema, ArgType
from mbot.core.plugins import plugin, PluginCommandContext, PluginCommandResponse
from .event import command, download_by_code, download_completed

server = mbot_api
_LOGGER = logging.getLogger(__name__)


@plugin.command(name='update_rate', title='更新并下载', desc='更新学习资料榜单数据，并提交下载,请注意是否已进行过配置', icon='',
                run_in_background=True)
def echo(ctx: PluginCommandContext):
    try:
        command()
    except Exception as e:
        _LOGGER.error(e, exc_info=True)
        return PluginCommandResponse(False, f'创建数据源失败')
    return PluginCommandResponse(True, f'创建数据源成功')


@plugin.command(name='download', title='下载指定科目', desc='下载指定科目,如果科目不存在，则会进入想看科目列表', icon='',
                run_in_background=True)
def echo(
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


@plugin.command(name='hard_link_mdc', title='硬链并整理', desc='硬链并整理', icon='',
                run_in_background=True)
def echo(ctx: PluginCommandContext):
    try:
        download_completed()
    except Exception as e:
        _LOGGER.error(e, exc_info=True)
        return PluginCommandResponse(False, f'创建数据源失败')
    return PluginCommandResponse(True, f'创建数据源成功')