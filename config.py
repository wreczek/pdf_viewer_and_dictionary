import yaml
from dataclasses import dataclass, field

CONFIG_PATH = "env/main.yaml"


@dataclass
class AppConfig:
    upload_folder: str = field(default="documents")
    db_path: str = field(default="./db/familiar_words.csv")


def load_config():
    with open(CONFIG_PATH, "r") as config_file:
        config_data = yaml.safe_load(config_file)
        return AppConfig(**config_data)