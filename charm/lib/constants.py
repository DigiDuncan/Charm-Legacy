import importlib.resources as pkg_resources

import toml

import charm.data
from charm.lib.attrdict import AttrDict

frets = None
instruments = None
difficulties = None


def loadfrets(data):
    global frets
    fretsdict = data.get("frets", {})
    frets = AttrDict(fretsdict)


def loadinstruments(data):
    global instruments
    instrumentsdict = data.get("instruments", {})
    instruments = AttrDict(instrumentsdict)


def loaddifficulties(data):
    global difficulties
    difficultiesdict = data.get("difficulties", {})
    difficulties = AttrDict(difficultiesdict)


def load():
    # Load constants toml file
    data = toml.loads(pkg_resources.read_text(charm.data, "constants.toml"))
    loadfrets(data)
    loadinstruments(data)
    loaddifficulties(data)


load()
