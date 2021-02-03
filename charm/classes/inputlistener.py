from lasergame.classes.gameobject import GameObject


class InputListener(GameObject):
    __slots__ = []

    def update(self, gm, events, **kwargs):
        # If `/~ pressed, bedug toggle.
        if gm.input.DEBUG.pressed:
            gm.state.debug = not gm.state.debug
