import pygame

from digicolor import colors

from lasergame.classes.gameobject import GameObject
from lasergame.lib import conf
from lasergame.lib.pgutils import scale_rect


class CollidableGameObject(GameObject):
    __slots__ = []


    @property
    def uuid_offset(self):
        return 0

    @property
    def collision_box(self):
        return None

    def draw_hitbox(self, debugscreen):
        if self.showuuid:
            hitbox = scale_rect(self.collision_box, conf.settings.scale)
            pygame.draw.rect(debugscreen, colors.RED.rgb, hitbox, 1)

    def update(self, gm, **kwargs):
        self.showuuid = gm.input.SELECT.held and gm.state.debug

    def collide(self, other, **kwargs):
        pass

    def draw(self, debugscreen, **kwargs):
        self.draw_uuid(debugscreen, self.uuid_offset)
        self.draw_hitbox(debugscreen)
