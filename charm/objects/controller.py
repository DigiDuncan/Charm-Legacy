from lasergame.classes.gameobject import GameObject
from lasergame.lib.assets import images
from lasergame.lib.constants import zlayer


buttonmap = {
    "UP": ("buttons.dpad-up", None),
    "DOWN": ("buttons.dpad-down", None),
    "LEFT": ("buttons.dpad-left", None),
    "RIGHT": ("buttons.dpad-right", None),
    "A": ("buttons.a-on", "buttons.a-off"),
    "B": ("buttons.b-on", "buttons.b-off"),
    "X": ("buttons.x-on", "buttons.x-off"),
    "Y": ("buttons.y-on", "buttons.y-off"),
    "L": ("buttons.l-on", "buttons.l-off"),
    "R": ("buttons.r-on", "buttons.r-off"),
    "SELECT": ("buttons.select-on", "buttons.select-off"),
    "START": ("buttons.start-on", "buttons.start-off"),
}


class Controller(GameObject):
    __slots__ = ["buttons", "show"]

    def __init__(self):
        self.buttons = None
        self.show = False
        super().__init__(z=zlayer.DEBUG)

    def update(self, gm, events, **kwargs):
        self.buttons = {btn: gm.input.actions[btn].held for btn in buttonmap}
        self.show = gm.state.debug

    def draw(self, debugscreen, **kwargs):
        if not self.show:
            return
        surface = images.get("buttons.controller").copy()

        for name, (active, inactive) in buttonmap.items():
            if self.buttons[name]:
                if active is not None:
                    surface.blit(images.get(active), (0, 0))
            else:
                if inactive is not None:
                    surface.blit(images.get(inactive), (0, 0))

        debugscreen.blit(surface, self.center)
