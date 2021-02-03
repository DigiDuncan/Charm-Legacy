import pygame

from digicolor import colors

from lasergame.classes.collidablegameobject import CollidableGameObject
from lasergame.lib import constants
from lasergame.lib.constants import zlayer
from lasergame.lib.pgutils import write, draw_box
from lasergame.objects.projectiles.bullet import Bullet
from lasergame.objects.textbox import Textbox


class Box(CollidableGameObject):
    __slots__ = ["center", "width", "height", "color", "_hits"]

    def __init__(self, center: tuple, width = 25, height = 25, color = colors.CYAN.rgb):
        self.color = color
        self.width = width
        self.height = height
        self._hits = 0
        super().__init__(center=center, z=zlayer.ENEMY)

    @property
    def left(self):
        return self.x - int(self.width / 2)

    @property
    def top(self):
        return self.y - int(self.width / 2)

    @property
    def right(self):
        return self.left + self.width

    @property
    def bottom(self):
        return self.top + self.height

    @property
    def collision_box(self):
        return pygame.Rect(self.left, self.top, self.width, self.height)

    @property
    def uuid_offset(self):
        return (self.height / 2) + 3

    def update(self, gm, **kwargs):
        collisions = gm.collisions[self]
        for other in collisions:
            if isinstance(other, Bullet) and other.owner != self.uuid:
                self._hits += other.damage
                gm.discard(other)
                gm.add(Textbox((0, constants.game.height - 50), f"You've hit me for {self._hits} damage so far!", 5,
                               fontsettings = {"font": "m5x7"}, animationtype = "frombottom", animationspeed = 100,
                               name = "Box"))
                gm.state.score += other.damage * 10
        if gm.input.X.pressed:
            gm.add(Bullet((self.x - (self.height / 2), self.y), 270, owner = self.uuid, bullettype = "red"))
        super().update(gm=gm)

    def draw(self, screen, debugscreen, **kwargs):
        draw_box(screen, self.center, self.width, self.height, color = self.color)
        write(screen,
              (self.x, self.y - 8),
              str(self._hits),
              halign = "center")
        super().draw(debugscreen = debugscreen)
        return self.collision_box
