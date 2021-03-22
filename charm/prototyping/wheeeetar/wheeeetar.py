from pathlib import Path
import nygame
from nygame import joystick
from pygame import Rect
from pygame.constants import JOYAXISMOTION, JOYBALLMOTION, JOYBUTTONDOWN, JOYBUTTONUP, JOYHATMOTION
import pygame.image


def button_prop(i):
    def getter(self):
        return self.buttons[i]

    def setter(self, value):
        self.buttons[i] = value

    return property(getter, setter)


class Game(nygame.Game):
    buttonmap = [
        "green",    # Green Fret Button
        "red",      # Red Fret Button
        "blue",     # Blue Fret Button
        "yellow",   # Yellow Fret Button
        "orange",   # Orange Fret Button
        None,
        "select",   # Select Button / Star Power / -
        "start"     # Start Button / +
    ]

    def __init__(self):
        super().__init__()
        self.baseimg = pygame.image.load(Path(__file__).parent / "base.png")
        self.pressedimg = pygame.image.load(Path(__file__).parent / "pressed.png")

        nygame.joystick.init()
        self.joysticks = [joystick.Joystick(x) for x in range(joystick.get_count())]
        self.strumbar = 0
        self.joystick = (0, 0)
        self.tilt = 0
        self.whammy = -1
        self.buttons = [False] * 8

    def drawpressed(self, rect):
        self.surface.set_clip(rect)
        self.surface.blit(self.pressedimg, (0, 0))

    def drawbar(self, rect, value):
        self.surface.set_clip(None)
        sub = self.pressedimg.subsurface(rect)
        self.surface.blit(sub, rect.move(0, ((-value) - 1) * 100))

    def loop(self, events):
        for e in events:
            if e.type == JOYHATMOTION:
                # Strum bar / Joystick
                self.joystick = e.value
                self.strumbar = e.value[1]
            elif e.type == JOYBUTTONDOWN:
                if e.button in (0, 1, 2, 3, 4, 6, 7):
                    self.buttons[e.button] = True
            elif e.type == JOYBUTTONUP:
                if e.button in (0, 1, 2, 3, 4, 6, 7):
                    self.buttons[e.button] = False
            elif e.type == JOYAXISMOTION:
                if e.axis == 3:
                    self.tilt = e.value
                elif e.axis == 2:
                    self.whammy = e.value

        self.surface.set_clip(None)
        self.surface.blit(self.baseimg, (0, 0))
        if self.green:
            self.drawpressed(Rect(39, 22, 98, 132))
        if self.red:
            self.drawpressed(Rect(140, 22, 98, 132))
        if self.yellow:
            self.drawpressed(Rect(247, 22, 98, 132))
        if self.blue:
            self.drawpressed(Rect(349, 22, 98, 132))
        if self.orange:
            self.drawpressed(Rect(458, 22, 98, 132))
        if self.joystick[0] == -1:
            self.drawpressed(Rect(414, 253, 49, 31))
        if self.joystick[0] == 1:
            self.drawpressed(Rect(487, 254, 44, 31))
        if self.joystick[1] == -1:
            self.drawpressed(Rect(464, 281, 24, 43))
        if self.joystick[1] == 1:
            self.drawpressed(Rect(463, 218, 25, 42))
        if self.strumbar == 1:
            self.drawpressed(Rect(95, 190, 242, 67))
        if self.strumbar == -1:
            self.drawpressed(Rect(95, 267, 242, 67))
        if self.select:
            self.drawpressed(Rect(102, 360, 209, 203))
        if self.start:
            self.drawpressed(Rect(338, 387, 91, 115))
        self.drawbar(Rect(639, 491, 40, 14), (self.tilt * -2) - 1)
        self.drawbar(Rect(745, 489, 46, 17), self.whammy)
        # print(self.tilt)


for i, name in enumerate(Game.buttonmap):
    if name is None:
        continue
    setattr(Game, name, button_prop(i))

Game().run()
