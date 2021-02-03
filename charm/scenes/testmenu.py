import pygame

from digicolor import colors

from lasergame.classes.menu import Menu, SceneMenuItem, PlaceholderMenuItem
from lasergame.lib import conf
from lasergame.lib.pgutils import write


class TestMenu(Menu):
    def __init__(self, *, game):
        super().__init__(
            game,
            conf.game.center,
            items = [
                SceneMenuItem(game, "back", "BACK TO MAIN MENU", scene = "mainmenu"),
                PlaceholderMenuItem(game, "p1", "PLACEHOLDER 1"),
                PlaceholderMenuItem(game, "p2", "PLACEHOLDER 2"),
                PlaceholderMenuItem(game, "p3", "PLACEHOLDER 3"),
                PlaceholderMenuItem(game, "p4", "PLACEHOLDER 4"),
                PlaceholderMenuItem(game, "p5", "PLACEHOLDER 5")
            ],
            cursorsettings = {
                "color": colors.WHITE.rgb,
                "width": 8,
                "height": 8,
                "direction": "right"
            },
            fontsettings = {
                "color": colors.WHITE.rgb,
                "align": "center",
                "antialias": False,
                "font": "SinsGold",
                "size": 24
            }
        )

    def draw(self, **kwargs):
        super().draw()
        write(self.screen, (0, -50), "LaserGame",
              antialias = False,
              font = "EndlessBossBattleRegular",
              size = 24,
              halign = "center",
              valign = "center",
              screen_halign = "center",
              screen_valign = "center")


pygame.quit()
