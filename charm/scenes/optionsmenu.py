import pygame

from digicolor import colors

from lasergame.classes.menu import Menu, SceneMenuItem, IntValueMenuItem, BoolValueMenuItem
from lasergame.lib import conf
from lasergame.lib.pgutils import write


class OptionsMenu(Menu):
    def __init__(self, *, game):
        super().__init__(
            game,
            conf.game.center,
            items = [
                IntValueMenuItem(game, "framerate", "FRAMERATE", "framerate", 60, textoverrides = {0: "UNLOCKED", 69: "NICE"}),
                # Scale does not change.
                IntValueMenuItem(game, "scale", "SCALE", "scale", 4, minimum = 1, maximum = 5),
                # Nor does debug.
                BoolValueMenuItem(game, "debug", "DEBUG", "debug", True),
                SceneMenuItem(game, "back", "BACK TO MAIN MENU", scene = "mainmenu")
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
              valign = "center",
              halign = "center",
              screen_halign = "center",
              screen_valign = "center")


pygame.quit()
