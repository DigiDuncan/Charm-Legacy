import pygame
from pygame.surface import Surface


def gradientRect(left_color, right_color, target_rect):
    """Draw a horizontal-gradient filled rectangle covering <target_rect>"""
    color_rect = pygame.Surface((2, 2), pygame.SRCALPHA)  # tiny! 2x2 bitmap
    pygame.draw.line(color_rect, left_color,  (0, 0), (0, 1))  # left color line
    pygame.draw.line(color_rect, right_color, (1, 0), (1, 1))  # right color line
    color_rect = pygame.transform.smoothscale(color_rect, (target_rect.width, target_rect.height))  # stretch!
    return color_rect


def stacksurfs(surf1: Surface, surf2: Surface, gap = 0) -> Surface:
    if surf2 is None:
        return surf1
    if surf1 is None:
        return surf2

    width = max(surf1.get_width(), surf2.get_width())
    height = surf1.get_height() + surf2.get_height() + gap
    yoffset = surf1.get_height() + gap

    newsurf = pygame.Surface((width, height))
    newsurf.blit(surf1, (0, 0))
    newsurf.blit(surf2, (0, yoffset))

    return newsurf
