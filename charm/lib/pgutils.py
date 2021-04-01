import pygame


def gradientRect(left_color, right_color, target_rect):
    """Draw a horizontal-gradient filled rectangle covering <target_rect>"""
    color_rect = pygame.Surface((2, 2), pygame.SRCALPHA)  # tiny! 2x2 bitmap
    pygame.draw.line(color_rect, left_color,  (0, 0), (0, 1))  # left color line
    pygame.draw.line(color_rect, right_color, (1, 0), (1, 1))  # right color line
    color_rect = pygame.transform.smoothscale(color_rect, (target_rect.width, target_rect.height))  # stretch!
    return color_rect
