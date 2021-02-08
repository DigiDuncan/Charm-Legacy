from dataclasses import dataclass


@dataclass
class Layout:
    name: str
    inputs: list
    images: dict
