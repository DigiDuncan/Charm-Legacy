import importlib.resources as pkg_resources

import toml
import addict

import charm.data

frets = None
instruments = None
difficulties = None


def loadfrets(data):
    global frets
    fretsdict = data.get("frets", {})
    frets = addict(fretsdict)


def loadinstruments(data):
    global instruments
    instrumentsdict = data.get("instruments", {})
    instruments = addict(instrumentsdict)


def loaddifficulties(data):
    global difficulties
    difficultiesdict = data.get("difficulties", {})
    difficulties = addict(difficultiesdict)


def load():
    # Load constants toml file
    data = toml.loads(pkg_resources.read_text(charm.data, "constants.toml"))
    loadfrets(data)
    loadinstruments(data)
    loaddifficulties(data)


load()
