from mbot.external.downloadclient import DownloadClientManager

from plugins.xx.base_config import get_base_config, ConfigType


class DownloadClient:
    client_name: str
    client: None
    download_manager: DownloadClientManager = DownloadClientManager()

    def __init__(self, client_name: str):
        self.client_name = client_name
        self.download_manager.init(client_configs=get_base_config(ConfigType.Download_Client))
        self.client = self.get_client(client_name)

    def get_client(self, client_name):
        if client_name:
            return self.download_manager.get(client_name)
        else:
            return self.download_manager.default()

    def download_from_file(self, torrent_path, save_path, category):
        return self.client.download_from_file(torrent_filepath=torrent_path, savepath=save_path, category=category)

    def download_from_url(self, torrent_url, save_path, category):
        return self.client.download_from_url(url=torrent_url, savepath=save_path, category=category)
