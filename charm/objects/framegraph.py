import pygame
from digicolor import colors

from lasergame.classes.gameobject import GameObject
from lasergame.lib.constants import zlayer
from lasergame.lib.utils import clamp
from lasergame.lib.pgutils import write


colorlist = []

# This genenerates a list of rgb tuples fading between red to green,
# passing through orange and yellow. It starts at (255, 0, 0)
# [or (0xFF, 0x00, 0x00)], fades G from 0 -> 255 for 30 colors,
# then fades R from 255 -> 0 for 30 colors, resulting in 61 colors,
# from index 0 (red) to index 60 (green).
for i in range(61):
    r = 0
    g = 0
    if i < 30:
        r = 255
        g = int(255 / 30 * i)
    if 61 > i >= 30:
        r = int(255 / 30 * (30 - (i - 30)))
        g = 255
    if i == 61:
        r = 0
        g = 255
    colorlist.append((r, g, 0))


class FrameGraph(GameObject):
    __slots__ = ["_fps", "show", "surface", "object_count", "collision_count"]

    def __init__(self):
        self._fps = 60
        self.show = False
        self.surface = pygame.Surface((100, 61), flags=pygame.SRCALPHA)
        self.object_count = 0
        self.collision_count = 0
        super().__init__(z=zlayer.DEBUG)

    @property
    def color(self):
        return colorlist[clamp(0, int(self._fps), 60)]

    def update(self, gm, clock, **kwargs):
        self.show = gm.state.debug
        self._fps = clock.get_fps()
        self.object_count = len(gm)
        self.collision_count = len(gm.collisions)

    def draw(self, debugscreen, **kwargs):
        # Every tick, scroll the surface on pixel to the left,
        # then place a new pixel at the top-right for 60 FPS or above,
        # and one pixel down from the top for every frame under 60
        # the current FPS is.
        if not self.show:
            return
        self.surface.scroll(dx=-1)
        for i in range(61):
            self.surface.set_at((99, i), (0, 0, 0, 0))
        self.surface.set_at((99, (60 - int(self._fps))), self.color)

        debugscreen.blit(self.surface, (debugscreen.get_width() - self.surface.get_width(), 3))
        # Create debug information.
        write(debugscreen,
              (-8, 8 + self.surface.get_height()),
              f"{self._fps:0.2f}",
              color=colors.LIGHT_GREEN.rgb,
              halign="right",
              screen_halign="right")
        write(debugscreen,
              (-8, 24 + self.surface.get_height()),
              f"{self.object_count} objects",
              color=colors.LIGHT_GREEN.rgb,
              halign="right",
              screen_halign="right")
        write(debugscreen,
              (-8, 40 + self.surface.get_height()),
              f"{self.collision_count} collisions",
              color=colors.LIGHT_GREEN.rgb,
              halign="right",
              screen_halign="right")
