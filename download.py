from mbot.external.downloadclient import DownloadClientManager, DownloadClient
import yaml

download_manager = DownloadClientManager()


def get_config():
    yml_path = '/data/conf/base_config.yml'
    data = yaml.load(open(yml_path, 'r', encoding='utf-8'), Loader=yaml.FullLoader)
    download_client = data['download_client']
    return download_client


client_configs = get_config()
download_manager.init(client_configs=client_configs)
client = None


def get_client(client_name):
    global client
    if not client:
        if client_name:
            client = download_manager.get(client_name)
        else:
            client = download_manager.default()
    else:
        current_client_name = client.get_client_name()
        if current_client_name != current_client_name:
            client = download_manager.get(client_name)
    return client


def download(torrent_path, save_path, category, client_name: None):
    current_client = get_client(client_name)
    if current_client:
        return current_client.download_from_file(torrent_filepath=torrent_path, savepath=save_path, category=category)
    return False


def list_downloading_torrents(client_name):
    current_client = get_client(client_name)
    if current_client:
        downloading_torrents = current_client.download_torrents()
        torrents = []
        for torrent_hash in downloading_torrents:
            torrents.append(downloading_torrents[torrent_hash])
        return torrents
    return None
