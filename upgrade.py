from mbot.core.plugins.pluginloader import PluginLoader
from mbot.core import MovieBot

movie_bot = MovieBot()
plugin_loader = PluginLoader(plugin_folder='/data/plugins', mbot=movie_bot)


def upgrade():
    # 卸载
    plugin_loader.uninstall('jav_bot')
    # 安装
    plugin_loader.install(download_url='https://gitee.com/orek1/jav_bot/repository/archive/master.zip')
    # 加载
    plugin_loader.setup('/data/plugins/jav_bot')
