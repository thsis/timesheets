import os
from configobj import ConfigObj
from pathlib import Path


def get_project_root() -> Path:
    """Returns project root folder."""
    return Path(__file__).parent.parent


def get_path(*args):
    return os.path.join(get_project_root(), *args)


def get_config(section=None):
    path = os.path.join(get_project_root(), "config.ini")
    out = dict(ConfigObj(path))
    if section:
        out = out[section]
    return out

