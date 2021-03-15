from dataclasses import dataclass
from typing import Dict, List, Tuple

from charm.lib.njson import jsonable


@jsonable
@dataclass
class Gamemode:
    name: str
    instruments: List[str]
    lane_count: int
    image_folder: str
    note_names: Dict[int, str]
    note_flags: List[str]
    note_positions: Dict[int, int]
    sprite_size: Tuple[int, int]
    diff_names: Dict[int, str]
