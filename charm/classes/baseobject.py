import pygame


class BaseObject:
    __slots__ = ["_rect"]

    def __init__(self, *,
                 w=None, h=None, width=None, height=None, size=None,
                 x=None, y=None,
                 left=None, centerx=None, right=None,
                 top=None, centery=None, bottom=None,
                 topleft=None, midtop=None, topright=None,
                 midleft=None, center=None, midright=None,
                 bottomleft=None, midbottom=None, bottomright=None):
        # Create a blank rectangle to store values
        self._rect = pygame.Rect(0, 0, 0, 0)

        # This checks to make sure you've provided the size arguments exactly once
        w_providers = [w, width, size]
        h_providers = [h, height, size]
        w_provider_count = len([p for p in w_providers if p is not None])
        h_provider_count = len([p for p in h_providers if p is not None])
        if w_provider_count > 1 or w_provider_count > 1:
            raise ValueError("Duplicate size arguments")
        if w_provider_count == 0 or h_provider_count == 0:
            raise ValueError("Missing size arguments")

        # Set the size (This must be set before setting x, y coordinates)
        if w is not None:
            self.w = w
        if h is not None:
            self.h = h
        if width is not None:
            self.width = width
        if height is not None:
            self.height = height
        if size is not None:
            self.size = size

        x_providers = [x, left, centerx, right, topleft, midtop, topright, midleft, center, midright, bottomleft, midbottom, bottomright]
        y_providers = [y, top, centery, bottom, topleft, midtop, topright, midleft, center, midright, bottomleft, midbottom, bottomright]
        x_provider_count = len([p for p in x_providers if p is not None])
        y_provider_count = len([p for p in y_providers if p is not None])
        if x_provider_count > 1 or y_provider_count > 1:
            raise ValueError("Duplicate coordinate arguments")
        if x_provider_count == 0 or y_provider_count == 0:
            raise ValueError("Missing coordinate arguments")

        # Set the x, y coordinates
        if x is not None:
            self.x = x
        if y is not None:
            self.y = y

        if left is not None:
            self.left = left
        if centerx is not None:
            self.centerx = centerx
        if right is not None:
            self.right = right

        if top is not None:
            self.top = top
        if centery is not None:
            self.centery = centery
        if bottom is not None:
            self.bottom = bottom

        if topleft is not None:
            self.topleft = topleft
        if midtop is not None:
            self.midtop = midtop
        if topright is not None:
            self.topright = topright
        if midleft is not None:
            self.midleft = midleft
        if center is not None:
            self.center = center
        if midright is not None:
            self.midright = midright
        if bottomleft is not None:
            self.bottomleft = bottomleft
        if midbottom is not None:
            self.midbottom = midbottom
        if bottomright is not None:
            self.bottomright = bottomright

    @property
    def w(self):
        return self._rect.w

    @w.setter
    def w(self, value):
        self._rect.w = value

    @property
    def h(self):
        return self._rect.h

    @h.setter
    def h(self, value):
        self._rect.h = value

    @property
    def height(self):
        return self._rect.height

    @height.setter
    def height(self, value):
        self._rect.height = value

    @property
    def width(self):
        return self._rect.width

    @width.setter
    def width(self, value):
        self._rect.width = value

    @property
    def size(self):
        return self._rect.size

    @size.setter
    def size(self, value):
        self._rect.size = value

    @property
    def x(self):
        return self._rect.x

    @x.setter
    def x(self, value):
        self._rect.x = value

    @property
    def y(self):
        return self._rect.y

    @y.setter
    def y(self, value):
        self._rect.y = value

    @property
    def left(self):
        return self._rect.left

    @left.setter
    def left(self, value):
        self._rect.left = value

    @property
    def centerx(self):
        return self._rect.centerx

    @centerx.setter
    def centerx(self, value):
        self._rect.centerx = value

    @property
    def right(self):
        return self._rect.right

    @right.setter
    def right(self, value):
        self._rect.right = value

    @property
    def top(self):
        return self._rect.top

    @top.setter
    def top(self, value):
        self._rect.top = value

    @property
    def centery(self):
        return self._rect.centery

    @centery.setter
    def centery(self, value):
        self._rect.centery = value

    @property
    def bottom(self):
        return self._rect.bottom

    @bottom.setter
    def bottom(self, value):
        self._rect.bottom = value

    @property
    def topleft(self):
        return self._rect.topleft

    @topleft.setter
    def topleft(self, value):
        self._rect.topleft = value

    @property
    def midtop(self):
        return self._rect.midtop

    @midtop.setter
    def midtop(self, value):
        self._rect.midtop = value

    @property
    def topright(self):
        return self._rect.topright

    @topright.setter
    def topright(self, value):
        self._rect.topright = value

    @property
    def midleft(self):
        return self._rect.midleft

    @midleft.setter
    def midleft(self, value):
        self._rect.midleft = value

    @property
    def center(self):
        return self._rect.center

    @center.setter
    def center(self, value):
        self.center = value

    @property
    def midright(self):
        return self._rect.midright

    @midright.setter
    def midright(self, value):
        self._rect.midright = value

    @property
    def bottomleft(self):
        return self._rect.bottomleft

    @bottomleft.setter
    def bottomleft(self, value):
        self._rect.bottomleft = value

    @property
    def midbottom(self):
        return self._rect.midbottom

    @midbottom.setter
    def midbottom(self, value):
        self._rect.midbottom = value

    @property
    def bottomright(self):
        return self._rect.bottomright

    @bottomright.setter
    def bottomright(self, value):
        self._rect.bottomright = value
