import datetime
import os
import shutil
import zipfile

import requests
import logging
from json import load

_LOGGER = logging.getLogger(__name__)
download_url = 'https://github.com/or3ki/jav_bot/archive/refs/heads/master.zip'
plugin_folder = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
zip_path = f"{plugin_folder}/jav_bot.zip"
extract_path = f"{plugin_folder}/jav_bot_new_{str(round(datetime.datetime.now().timestamp()))}"
dst = f"{plugin_folder}/jav_bot"
manifest_url = 'https://raw.githubusercontent.com/or3ki/jav_bot/master/manifest.json'


def upgrade_project(proxies, retry_time):
    if retry_time > 3:
        _LOGGER.error("尝试拉取项目3次失败,在线更新学习工具失败")
        return False
    try:
        res = requests.get(download_url, proxies=proxies)
    except Exception as e:
        upgrade_project(proxies, retry_time + 1)

    with open(zip_path, "wb") as code:
        code.write(res.content)
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)
    manifest_path = find_path(extract_path, 'manifest.json')
    plugin_path = os.path.split(manifest_path)[0]
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.move(plugin_path, dst)
    os.remove(zip_path)
    shutil.rmtree(extract_path)
    return True


def find_path(path, filename):
    if not path or not filename:
        return
    if not os.path.exists(path):
        return
    filename = str(filename).lower()
    if os.path.isfile(path):
        if str(path).lower().endswith(filename):
            return path
        else:
            return
    for p, dir_list, file_list in os.walk(path):
        for f in file_list:
            fp = os.path.join(p, f)
            if f.lower() == filename:
                return fp
    return


def check_update(proxies):
    with open('manifest.json', 'r', encoding='utf-8') as fp:
        json_data = load(fp)
        local_version = json_data['version']
    res = requests.get(manifest_url, proxies=proxies)
    json = res.json()
    latest_version = json['version']
    if local_version != latest_version:
        return True
    return False
