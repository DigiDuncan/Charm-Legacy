from .fontmanager import FontManager
from .imagemanager import ImageManager
from .soundmanager import SoundManager

__all__ = ["fonts", "images", "sounds"]

fonts = FontManager()
images = ImageManager()
sounds = SoundManager()
