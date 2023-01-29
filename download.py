from mbot.external.downloadclient import DownloadClientManager, DownloadClient
import yaml


def get_config():
    yml_path = '/data/conf/base_config.yml'
    data = yaml.load(open(yml_path, 'r', encoding='utf-8'), Loader=yaml.FullLoader)
    download_client = data['download_client']
    return download_client


def get_client(client_name):
    download_manager = DownloadClientManager()
    client_configs = get_config()
    download_manager.init(client_configs=client_configs)
    if client_name:
        client = download_manager.get(client_name)
        return client
    else:
        client = download_manager.default()
        return client
    return None


def download(torrent_path, save_path, category, client_name: None):
    client = get_client(client_name)
    if client:
        return client.download_from_file(torrent_filepath=torrent_path, savepath=save_path, category=category)
    return False


def list_downloading_torrents(client_name):
    client = get_client(client_name)
    if client:
        return client.download_torrents()
    return None


def list_completed_torrents(client_name):
    client = get_client(client_name)
    if client:
        return client.completed_torrents()
    return None
