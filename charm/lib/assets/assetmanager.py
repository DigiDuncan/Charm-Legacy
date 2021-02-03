import importlib
import importlib.resources


class AssetNotFoundError(Exception):
    def __init__(self, module_path, name):
        full_path = f"{module_path}/{name}"
        super().__init__(f"Unable to load asset: {full_path!r}")


class AssetManager:
    def __init__(self, root, ext):
        self.root = root
        self.ext = ext

    def parse_path(self, path):
        subpath, _, filename = path.rpartition(".")
        module_path = self.root
        if subpath:
            module_path += "." + subpath
        filename = f"{filename}.{self.ext}"
        return module_path, filename

    def open_binary(self, name):
        module_path, filename = self.parse_path(name)
        try:
            module = importlib.import_module(module_path)
        except ModuleNotFoundError:
            raise AssetNotFoundError(module_path, filename)
        try:
            f = importlib.resources.open_binary(module, filename)
        except FileNotFoundError:
            raise AssetNotFoundError(module_path, filename)
        return f
