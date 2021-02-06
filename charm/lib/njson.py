import typing
import dataclasses

from json import JSONEncoder

__all__ = ("jsonable", "NEncoder")


def parse_field(j, ftype):
    from_json = getattr(ftype, "from_json", None)
    if callable(from_json):
        return ftype.from_json(j)
    if typing.get_origin(ftype) == list:
        inner_type = typing.get_args(ftype)[0]
        return [parse_field(i, inner_type) for i in j]
    return j


def jsonable(cls):
    """Decorator to make dataclasses jsonable"""
    def to_json(self):
        """Return a json compatible representation of a dataclass"""
        return self.__dict__

    @classmethod
    def from_json(cls, j):
        """Parse a json representation of this class"""
        fields = dataclasses.fields(cls)
        return cls(**{f.name: parse_field(j[f.name], f.type) for f in fields})

    # Monkey patch to_json and from_json methods onto the dataclass
    setattr(cls, "to_json", to_json)
    setattr(cls, "from_json", from_json)

    return cls


class NEncoder(JSONEncoder):
    """Custom json encoder that will call obj.to_json() if json can't serialize the object"""
    def default(self, obj):
        to_json = getattr(obj, "to_json", None)
        if callable(to_json):
            return obj.to_json()
        return super().default(obj)
