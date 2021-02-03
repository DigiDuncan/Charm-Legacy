import pygame

from lasergame.classes.collidablegameobject import CollidableGameObject
from lasergame.lib.constants import zlayer


class Projectile(CollidableGameObject):
    __slots__ = ["owner", "speed"]

    def __init__(self, center: tuple, *, owner, speed = 180):
        self.owner = owner
        self.speed = speed
        super().__init__(center=center, z=zlayer.PROJECTILE)

    @property
    def color(self):
        raise NotImplementedError

    @property
    def damage(self):
        raise NotImplementedError

    @property
    def uuid_offset(self):
        raise NotImplementedError

    def update(self, clock, screen, gm, **kwargs):
        if not self.is_on_screen(screen):
            gm.discard(self)
        super().update(gm=gm)

    def is_on_screen(self, screen):
        raise NotImplementedError

    @property
    def left(self):
        raise NotImplementedError

    @property
    def top(self):
        raise NotImplementedError

    @property
    def right(self):
        raise NotImplementedError

    @property
    def bottom(self):
        raise NotImplementedError

    @property
    def collision_box(self):
        return pygame.Rect(self.left, self.top, self.right - self.left, self.bottom - self.top)

    def draw(self, screen, debugscreen, **kwargs):
        super().draw(debugscreen = debugscreen)
        return self.collision_box
