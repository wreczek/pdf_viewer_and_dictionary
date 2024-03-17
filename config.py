import os
from dataclasses import dataclass, field

import yaml

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "env", "main.yaml")


@dataclass
class AppConfig:
    upload_folder: str = field(default=os.path.join(BASE_DIR, 'app', "documents"))
    static_folder: str = field(default=os.path.join(BASE_DIR, 'static'))
    words_csv_path: str = field(default=os.path.join(BASE_DIR, "db", "familiar_words.csv"))


def load_config():
    with open(CONFIG_PATH) as config_file:
        config_data = yaml.safe_load(config_file)
        return AppConfig(**config_data)
