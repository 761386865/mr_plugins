from enum import Enum

import yaml

yml_path: str = 'base_config.yml'


class ConfigType(str, Enum):
    Download_Client = 'download_client'
    Notify_Channel = 'notify_channel'


def get_base_config(config_type: ConfigType):
    data = yaml.load(open(yml_path, 'r', encoding='utf-8'), Loader=yaml.FullLoader)
    configs = data[config_type]
    return configs
