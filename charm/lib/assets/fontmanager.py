import io
from functools import lru_cache

import pygame

from lasergame.lib.assets.assetmanager import AssetManager


class FontManager(AssetManager):
    def __init__(self):
        super().__init__("lasergame.data.fonts", "ttf")

    @lru_cache(maxsize=None)
    def get(self, name=None, size=None):
        """Load a font

        The font will be loaded from cache, if available

        font = fonts.get()
        font = fonts.get(size=16)
        font = fonts.get("FutilePro", size=16)
        """

        if size is None:
            size = 16

        # Special exception for default font
        if name is None:
            return pygame.font.Font(pygame.font.get_default_font(), size)

        # pygame's Font constructor doesn't load file handles properly, so we have to wrap them in a BytesIO.
        with self.open_binary(name) as f:
            data = io.BytesIO(f.read())
        font = pygame.font.Font(data, size)
        return font
