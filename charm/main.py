import pygame
from charm.lib import nygame

from digicolor import colors

from charm.lib import conf, constants
from charm.lib.display import display
from charm.lib.inputmanager import InputManager
from charm.lib.pgutils import write
from charm.scenes.gameloop import GameLoop
from charm.scenes.mainmenu import MainMenu
from charm.scenes.optionsmenu import OptionsMenu
from charm.scenes.testmenu import TestMenu


class Game():
    __slots__ = ["active", "scenes", "running", "paused", "clock", "input", "screen", "debugscreen"]

    def __init__(self):
        self.active = None
        self.scenes = {}
        self.running = True
        self.paused = False
        self.clock = nygame.time.Clock()
        self.input = InputManager()
        self.input.load()

        # Create the screen.
        window_size = (conf.settings.windowwidth, conf.settings.windowheight)
        screen_size = (constants.game.width, constants.game.height)

        display.set_mode(window_size)

        self.screen = display.add_layer(pygame.Surface(screen_size))
        self.debugscreen = display.add_layer(pygame.Surface(display.size, flags=pygame.SRCALPHA))

    def run(self):
        pygame.init()

        # Window title.
        pygame.display.set_caption("Charm v0 by DigiSoft")

        self.scenes = {
            "mainmenu": MainMenu(game = self),
            "gameloop": GameLoop(game = self),
            "optionsmenu": OptionsMenu(game = self),
            "testmenu": TestMenu(game = self)
        }
        self.switch_scene("mainmenu")

        while self.running:
            # Window close button
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.quit()

            # Get input
            self.input.update(events=events)
            if self.input.FULLSCREEN.pressed:
                if display.fullscreen:
                    window_size = (conf.settings.windowwidth, conf.settings.windowheight)
                    display.set_mode((window_size))
                else:
                    display.set_mode((0, 0), fullscreen=True)
            # Run current scene's update function (or not if we're paused.)
            paused = self.paused
            if not self.paused:
                self.active.update(events=events)
            if paused and self.input.START.pressed:
                self.unpause()
            # Fill the background
            self.screen.fill(colors.BLACK.rgb)
            self.debugscreen.fill((0, 0, 0, 0))
            # Run current scene's draw function
            self.active.draw()
            # Write "PAUSED" on the screen if we're, you know, paused.
            if self.paused:
                write(self.screen,
                      (0, 0),
                      "PAUSED",
                      halign = "center",
                      valign = "center",
                      screen_halign="center",
                      screen_valign="center",
                      font = "EndlessBossBattleRegular",
                      size = 32,
                      antialias = False)
            # Final draw stage
            display.flip()
            # Timing loop
            self.clock.tick_busy_loop(conf.settings.framerate)

    def switch_scene(self, name):
        # Sometimes the scenes don't get initialized quick enough.
        # Make sure we have scenes to switch to, and just return if we don't.
        if self.scenes is None or self.scenes == {}:
            return
        self.active = self.scenes[name]

    def pause(self):
        self.paused = True

    def unpause(self):
        self.paused = False

    def quit(self):
        self.running = False


def main():
    # Make a Game object and run it.
    g = Game()
    g.run()


# This is needed, or else calling `python -m <name>` will mean that main() is called twice.
if __name__ == "__main__":
    main()
