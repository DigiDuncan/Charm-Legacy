from typing import Literal

import pygame

from digicolor import colors

from lasergame.lib.assets import fonts, sounds


def render_text(text,
                *,
                color=colors.WHITE.rgb,
                antialias: bool = True,
                font=None,
                size=None,
                background=None):
    font_obj = fonts.get(font, size=size)
    text = str(text)
    textsurface = font_obj.render(text, antialias, color, background)
    return textsurface


def blit(dest: pygame.Surface,
         src: pygame.Surface,
         coords,
         halign: Literal["left", "center", "right"] = "left",
         valign: Literal["top", "center", "bottom"] = "top",
         screen_halign: Literal["left", "center", "right"] = "left",
         screen_valign: Literal["top", "center", "bottom"] = "top"):
    coords = align_rect(dest.get_rect(), src.get_rect(), coords, halign=halign, valign=valign, outer_halign=screen_halign, outer_valign=screen_valign)
    dest.blit(src, coords)
    return coords


def align_rect(
        outer: pygame.Rect,
        inner: pygame.Rect,
        coords,
        *,
        halign: Literal["left", "center", "right"] = "left",
        valign: Literal["top", "center", "bottom"] = "top",
        outer_halign: Literal["left", "center", "right"] = "left",
        outer_valign: Literal["top", "center", "bottom"] = "top"):
    """Calculate coordinates for an inner rectangle aligned to an outer rectangle"""
    x, y = coords

    if outer_halign == "left":
        pass
    elif outer_halign == "center":
        x = outer.centerx + x
    elif outer_halign == "right":
        x = outer.right + x

    if outer_valign == "top":
        pass
    elif outer_valign == "center":
        y = outer.centery + y
    elif outer_valign == "bottom":
        y = outer.bottom + y

    if halign == "left":
        inner.left = x
    elif halign == "center":
        inner.centerx = x
    elif halign == "right":
        inner.right = x

    if valign == "top":
        inner.top = y
    elif valign == "center":
        inner.centery = y
    elif valign == "bottom":
        inner.bottom = y

    return inner.topleft


def write(screen,
          coords,
          text,
          *,
          color=colors.WHITE.rgb,
          halign: Literal["left", "center", "right"] = "left",
          valign: Literal["top", "center", "bottom"] = "top",
          screen_halign: Literal["left", "center", "right"] = "left",
          screen_valign: Literal["top", "center", "bottom"] = "top",
          antialias: bool = True,
          font=None,
          size=None,
          background=None):
    textsurface = render_text(text, color=color, antialias=antialias, font=font, size=size, background=background)
    blit(screen, textsurface, coords, halign=halign, valign=valign, screen_halign=screen_halign, screen_valign=screen_valign)


def get_write_size(text, *, font=None, size=None):
    font_obj = fonts.get(font, size=size)
    return font_obj.size(text)


def draw_box(screen, center: tuple, width: int, height: int, *, color = colors.WHITE.rgb, thickness: int = 0):
    left = center[0] - int(width / 2)
    top = center[1] - int(height / 2)
    rect = pygame.Rect(left, top, width, height)
    return pygame.draw.rect(screen, color, rect, thickness)


def draw_triangle(screen, color, center, width, height, direction="right"):
    x, y = center
    left = x - (width / 2)
    right = x + (width / 2)
    top = y - (height / 2)
    bottom = y + (height / 2)
    middlex = x
    middley = y

    if direction == "up":
        u = (middlex, top)      # middle top (tip)
        v = (right, bottom)     # bottom right
        w = (left, bottom)      # bottom left
    elif direction == "right":
        u = (right, middley)    # middle right (tip)
        v = (left, bottom)      # bottom left
        w = (left, top)         # top left
    elif direction == "down":
        u = (middlex, bottom)   # middle bottom (tip)
        v = (left, top)         # top left
        w = (right, top)        # top right
    elif direction == "left":
        u = (left, middley)     # middle left (tip)
        v = (right, top)        # top right
        w = (right, bottom)     # bottom right
    else:
        raise ValueError("Unrecognized direction")
    uvw = (u, v, w)
    collision_box = pygame.draw.polygon(screen, color, uvw)
    return collision_box


def scale_rect(rect, factor):
    newrect = rect.inflate(rect.width * (factor - 1), rect.height * (factor - 1))
    newrect.x = rect.x * factor
    newrect.y = rect.y * factor
    return newrect


def play_sound(sound: str, channel = 0):
    ch = pygame.mixer.Channel(channel)
    snd = sounds.get(sound)
    ch.play(snd)
