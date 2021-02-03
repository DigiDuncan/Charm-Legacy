from functools import lru_cache

import pygame
from digicolor import colors

from lasergame.lib.assets.assetmanager import AssetManager


class ImageManager(AssetManager):
    def __init__(self):
        super().__init__("lasergame.data.images", "png")

    @lru_cache(maxsize=None)
    def get(self, name):
        """Load a named image

        The image will be loaded from cache, if available

        image = images.get("buttons.up")
        """
        with self.open_binary(name) as f:
            image = pygame.image.load(f)
        image.set_colorkey(colors.LIGHT_MAGENTA.rgb)
        return image
