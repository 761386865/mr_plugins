from mbot.external.downloadclient import DownloadClientManager
import yaml


class DownloadClient:
    yml_path: str = '/data/conf/base_config.yml'
    client_name: str
    client: None
    download_manager: DownloadClientManager = DownloadClientManager()

    def __init__(self, client_name: str):
        self.client_name = client_name
        self.download_manager.init(client_configs=self.get_config())
        self.client = self.get_client(client_name)

    def get_config(self):
        data = yaml.load(open(self.yml_path, 'r', encoding='utf-8'), Loader=yaml.FullLoader)
        download_client = data['download_client']
        return download_client

    def get_client(self, client_name):
        if client_name:
            return self.download_manager.get(client_name)
        else:
            return self.download_manager.default()

    def download(self, torrent_path, save_path, category):
        return self.client.download_from_file(torrent_filepath=torrent_path, savepath=save_path, category=category)


