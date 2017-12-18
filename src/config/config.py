import json
import os
import sys


def get_config_path():
    settings_path = ''

    # determine if application is a script file or frozen exe
    if getattr(sys, 'frozen', False):
        settings_path = os.path.dirname(sys.executable)
    elif __file__:
        settings_path = os.path.dirname(__file__)

    settings_path = os.path.join(settings_path)
    settings_path = os.path.abspath(settings_path)

    return settings_path


dir = get_config_path()
confing_path = os.path.join(dir, 'config', 'config.json')


def load_config():
    with open(confing_path, 'r') as config:
        data = json.load(config)
        return data


def create_config(settings):
    with open(confing_path, 'w') as config:
        json.dump(
            settings,
            config,
            sort_keys=True,
            indent=4,
            separators=(',', ':')
        )


if not confing_path:
    create_config()
