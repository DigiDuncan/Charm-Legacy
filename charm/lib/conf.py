import importlib.resources as pkg_resources

import toml

import lasergame.data
from lasergame.lib.attrdict import AttrDict
from lasergame.lib.constants import game


settings = None


def loadsettings(data):
    global settings
    settingsdict = data.get("settings", {})
    # make all names lowercase
    settingsdict = {name.lower(): value for name, value in settingsdict.items()}
    # create the enum
    settings = AttrDict(settingsdict)
    if not isinstance(settings.scale, int):
        raise ValueError("Scale is not an integer.")
    settings.windowwidth = game.width * settings.scale
    settings.windowheight = game.height * settings.scale


def load():
    # Load constants toml file
    data = toml.loads(pkg_resources.read_text(lasergame.data, "conf.toml"))
    loadsettings(data)


load()
