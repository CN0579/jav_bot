from qbittorrentapi import Client
import yaml

qb: Client = None


def get_qb_config(qb_name):
    yml_path = '/data/conf/base_config.yml'
    data = yaml.load(open(yml_path, 'r', encoding='utf-8'), Loader=yaml.FullLoader)
    download_client = data['download_client']
    if qb_name:
        for client in download_client:
            if client['name'] == qb_name and client['type'] == 'qbittorrent':
                return client
    else:
        for client in download_client:
            if client['is_default'] and client['type'] == 'qbittorrent':
                return client
        for client in download_client:
            if client['type'] == 'qbittorrent':
                return client
    return None


def login_qb(qb_name):
    global qb
    client_config = get_qb_config(qb_name)
    if client_config:
        qb = Client(host=client_config['url'], username=client_config['username'], password=client_config['password'])
        try:
            qb.auth_log_in()
        except Exception as e:
            return False
        return True
    return False


def list_completed_unlink_torrents():
    torrent_list = qb.torrents_info(status_filter='completed')
    filter_list = list(filter(lambda x: 'unlink' in x.tags, torrent_list))
    return filter_list


def download(torrent_path, save_path, category):
    torrent_file = open(torrent_path, 'rb')
    return qb.torrents_add(torrent_files=[torrent_file], save_path=save_path, category=category, tags='unlink')
