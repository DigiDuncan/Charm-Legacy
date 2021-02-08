import importlib.resources as pkg_resources

import toml

import charm.data
from charm.lib.attrdict import AttrDict

frets = None


def loadfrets(data):
    global frets
    fretsdict = data.get("frets", {})
    # make all names lowercase
    fretsdict = {name.lower(): value for name, value in fretsdict.items()}
    # create the enum
    frets = AttrDict(fretsdict)


def load():
    # Load constants toml file
    data = toml.loads(pkg_resources.read_text(charm.data, "constants.toml"))
    loadfrets(data)


load()
