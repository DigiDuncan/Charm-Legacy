from functools import lru_cache

import pygame

from lasergame.lib.assets.assetmanager import AssetManager


class SoundManager(AssetManager):
    def __init__(self):
        super().__init__("lasergame.data.sounds", "wav")

    @lru_cache(maxsize=None)
    def get(self, name):
        """Load a named sound

        The sound will be loaded from cache, if available

        sound = sounds.get("laser-1")
        """
        with self.open_binary(name) as f:
            sound = pygame.mixer.Sound(f)
        return sound
