import uuid

from digicolor import colors

from lasergame.lib.pgutils import write
from lasergame.lib.conf import settings


class GameObject:
    __slots__ = ["center", "z", "uuid", "showuuid"]

    def __init__(self, center=(0, 0), z=0):
        self.center = center
        self.z = z
        self.uuid = uuid.uuid4()
        self.showuuid = False

    @property
    def safecenter(self):
        return (int(self.center[0]), int(self.center[1]))

    @property
    def x(self):
        return self.center[0]

    @x.setter
    def x(self, value):
        self.center = (value, self.center[1])

    @property
    def y(self):
        return self.center[1]

    @y.setter
    def y(self, value):
        self.center = (self.center[0], value)

    @property
    def safex(self):
        return self.safecenter[0]

    @property
    def safey(self):
        return self.safecenter[1]

    def draw_uuid(self, screen, yoffset = 0):
        if self.showuuid:
            x, y = self.center
            coords = x * settings.scale, (y - yoffset) * settings.scale
            write(screen,
                  coords,
                  (str(self.uuid)[:8] + "..."),
                  halign = "center",
                  valign = "bottom",
                  color = colors.CYAN.rgb,
                  antialias = False)

    def __hash__(self):
        return hash(self.uuid)
