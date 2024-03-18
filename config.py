import os
from dataclasses import dataclass, field

import yaml

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "env", "main.yaml")


@dataclass
class BaseConfig:
    upload_folder: str = field(default=os.path.join(BASE_DIR, 'app', "documents"))
    static_folder: str = field(default=os.path.join(BASE_DIR, 'static'))
    words_csv_path: str = field(default=os.path.join(BASE_DIR, "db", "familiar_words.csv"))


@dataclass
class DevelopmentConfig(BaseConfig):
    """TODO: finish implementation"""
    DEBUG: bool = True


@dataclass
class ProductionConfig(BaseConfig):
    """TODO: finish implementation"""
    DEBUG: bool = False


def load_config():
    env = os.getenv('FLASK_ENV', 'development')
    with open(CONFIG_PATH) as config_file:
        config_data = yaml.safe_load(config_file)

    if env == 'development':
        return DevelopmentConfig(**config_data)
    elif env == 'production':
        return ProductionConfig(**config_data)
    else:
        raise ValueError(f"Unsupported environment: {env}")
