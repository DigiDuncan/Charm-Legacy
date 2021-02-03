import importlib.resources as pkg_resources
import math
import random

import pygame

from digicolor import colors

import lasergame.data
from lasergame.classes.menu import Menu, SceneMenuItem, QuitMenuItem
from lasergame.lib import conf, nygame
from lasergame.lib.assets import images
from lasergame.lib.pgutils import write, render_text, blit


splashtexts = pkg_resources.read_text(lasergame.data, "splashes.txt").splitlines()


class MainMenu(Menu):
    __slots__ = ["splashtext", "logo"]

    def __init__(self, *, game):
        self.splashtext = random.choice(splashtexts).upper()
        self.logo = images.get("digisoft-small")
        self.start_time = nygame.time.get_ticks_sec()
        x, y = conf.game.center
        coords = x, y + 30
        super().__init__(
            game,
            coords,
            items = [
                SceneMenuItem(game, "start", "START GAME", scene = "gameloop"),
                SceneMenuItem(game, "options", "OPTIONS", scene = "optionsmenu"),
                SceneMenuItem(game, "test", "TEST MENU", scene = "testmenu"),
                QuitMenuItem(game, "quit", "QUIT TO DESKTOP")
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

    @property
    def current_time(self):
        return nygame.time.get_ticks_sec() - self.start_time

    def draw(self, **kwargs):
        super().draw()
        if self.current_time < 1.25:
            black = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
            black.fill(colors.BLACK.rgb)
            blit(self.screen, black, (0, 0))
            write(self.screen, (0, 40 * self.current_time - 100), "LaserGame",
                  antialias = False,
                  font = "EndlessBossBattleRegular",
                  size = 24,
                  halign = "center",
                  valign = "center",
                  screen_halign = "center",
                  screen_valign = "center")
        else:
            # Have a white flash with a fade lasting 0.5 seconds here.
            write(self.screen,
                  (3, 0),
                  nygame.time.get_ticks_sec(),
                  antialias = False,
                  font = "SinsGold",
                  size = 16,
                  color = colors.LIGHT_CYAN.rgb)
            splash = render_text(self.splashtext,
                                 antialias = False,
                                 font = "SinsGold",
                                 size = 16,
                                 color = colors.LIGHT_CYAN.rgb)
            # splash_rot = magnitude * sin(speed * time_elapsed)
            splash_rot = 3.75 * math.sin(5 * nygame.time.get_ticks_sec())
            splash = pygame.transform.rotate(splash, splash_rot)
            write(self.screen, (0, -50), "LaserGame",
                  antialias = False,
                  font = "EndlessBossBattleRegular",
                  size = 24,
                  halign = "center",
                  valign = "center",
                  screen_halign = "center",
                  screen_valign = "center")
            blit(self.screen, splash, (0, -25),
                 halign="center",
                 valign = "center",
                 screen_halign = "center",
                 screen_valign = "center")
            blit(self.screen, self.logo, (0, 0),
                 halign="center",
                 valign="bottom",
                 screen_halign="center",
                 screen_valign="bottom")


pygame.quit()
