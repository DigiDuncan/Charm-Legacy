from typing import Literal

from digicolor import colors

from lasergame.classes.gameobject import GameObject
from lasergame.lib import conf
from lasergame.lib.pgutils import draw_triangle, write, get_write_size
from lasergame.lib.utils import clamp


class MenuItem:
    def __init__(self, game, name, text):
        self.game = game
        self.name = name
        self.text = text

    @property
    def displaytext(self):
        return self.text


class SceneMenuItem(MenuItem):
    def __init__(self, game, name, text, *, scene):
        self.scene = scene
        super().__init__(game, name, text)

    @property
    def function(self):
        return self.game.switch_scene(self.scene)


class QuitMenuItem(MenuItem):
    @property
    def function(self):
        return self.game.quit()


class PlaceholderMenuItem(MenuItem):
    @property
    def function(self):
        pass


class ValueMenuItem(MenuItem):
    def __init__(self, game, name, text, value, default, *, textoverrides = {}, **kwargs):
        self.value = value
        self.default = default
        self._current = self.default
        self.textoverrides = textoverrides
        super().__init__(game, name, text)

    def increment(self):
        setattr(conf.settings, self.value, self._current)

    def decrement(self):
        setattr(conf.settings, self.value, self._current)

    @property
    def function(self):
        pass

    @property
    def displaytext(self):
        if self._current in self.textoverrides:
            currenttext = self.textoverrides[self._current]
        else:
            currenttext = self._current
        return f"< {self.text}: {currenttext} >"


class BoolValueMenuItem(ValueMenuItem):
    def toggle(self):
        self._current = not self._current

    def increment(self):
        self.toggle()
        super().increment()

    def decrement(self):
        self.toggle()
        super().increment()


class IntValueMenuItem(ValueMenuItem):
    def __init__(self, game, name, text, value, default, step = 1, minimum = 0, maximum = None, **kwargs):
        self.step = step
        self.min = minimum
        self.max = maximum
        super().__init__(game, name, text, value, default, **kwargs)

    def increment(self):
        self._current += self.step
        self._current = clamp(self.min, self._current, self.max)
        super().increment()

    def decrement(self):
        self._current -= self.step
        self._current = clamp(self.min, self._current, self.max)
        super().increment()


class Menu(GameObject):
    def __init__(self,
                 game,
                 center,
                 items: list,
                 *,
                 valign: Literal["top", "center", "bottom"] = "center",
                 cursorsettings: dict,
                 fontsettings: dict):
        self.game = game
        self.screen = game.screen
        self.center = center
        self.items = items
        self.valign = valign
        self.cursorsettings = cursorsettings
        self.fontsettings = fontsettings

        self.fontcolor = fontsettings.get("color", colors.WHITE.rgb)
        self.fontalign = fontsettings.get("align", "center")
        self.fontantialias = fontsettings.get("antialias", False)
        self.fontfont = fontsettings.get("font", None)
        self.fontsize = fontsettings.get("size", None)

        self.cursorcolor = cursorsettings.get("color", colors.WHITE.rgb)
        self.cursorwidth = cursorsettings.get("width", 8)
        self.cursorheight = cursorsettings.get("height", 8)
        self.cursordirection = cursorsettings.get("direction", "right")

        self.selected = 0

    @property
    def write_size(self):
        return get_write_size(self.items[self.selected].displaytext, font=self.fontfont, size=self.fontsize)

    @property
    def fontspacing(self):
        return self.write_size[1] - 2

    @property
    def selector_x_offset(self):
        return self.write_size[0] / 2 + 8

    @property
    def texttopY(self):
        return self.safey - (self.fontspacing * len(self.items) / 2)

    @property
    def cursorpos(self):
        return (self.x - self.selector_x_offset,
                self.texttopY + ((self.selected + 1) * self.fontspacing) - (self.fontspacing / 2))

    def update(self, **kwargs):
        # Scroll up and down the menu.
        if self.game.input.UP.pressed:
            self.selected -= 1
        if self.game.input.DOWN.pressed:
            self.selected += 1
        # Wrap the cursor around.
        self.selected = self.selected % len(self.items)
        # If we're selected on a ValueMenuItem, left and right decrement and increment its value.
        if isinstance(self.items[self.selected], ValueMenuItem):
            if self.game.input.LEFT.pressed:
                self.items[self.selected].decrement()
            if self.game.input.RIGHT.pressed:
                self.items[self.selected].increment()
        if self.game.input.START.pressed:
            self.items[self.selected].function

    def draw(self, **kwargs):
        # Write each menu option in order.
        for n, item in enumerate(self.items):
            coords = self.x, self.texttopY + (n * self.fontspacing)
            write(self.screen,
                  coords,
                  item.displaytext,
                  color = self.fontcolor,
                  halign = self.fontalign,
                  antialias = self.fontantialias,
                  font = self.fontfont,
                  size = self.fontsize)
        # Draw the cursor.
        draw_triangle(self.screen, self.cursorcolor, self.cursorpos,
                      self.cursorwidth, self.cursorheight, self.cursordirection)
