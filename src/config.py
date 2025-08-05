# config.py
import os
from configparser import ConfigParser
from typing import Dict

CONFIG_FILE = 'config.ini'

def load_config() -> Dict[str, str]:
    """Loads credentials from the config file and returns them as a dictionary."""
    if not os.path.exists(CONFIG_FILE):
        return {}
        
    config = ConfigParser()
    config.read(CONFIG_FILE)
    if 'Twitch' in config:
        return dict(config['Twitch'])
    return {}

def save_config(client_id: str, access_token: str, user_id: str, refresh_interval: int):
    """Saves credentials to the config file."""
    config = ConfigParser()
    config['Twitch'] = {
        'client_id': client_id,
        'access_token': access_token,
        'user_id': user_id,
        'refresh_interval': refresh_interval
    }
    with open(CONFIG_FILE, 'w') as f:
        config.write(f)