import nygame
from pygame.surface import Surface


def stacksurfs(surf1: Surface, surf2: Surface):
    width = max(surf1.get_width(), surf2.get_width())
    height = surf1.get_height() + surf2.get_height()
    yoffset = surf1.get_height()

    newsurf = Surface((width, height))
    newsurf.blit(surf1, (0, 0))
    newsurf.blit(surf2, (0, yoffset))


class MenuItem:
    def __init__(self, key: str, title: str, artist: str):
        self.key = key
        self.title = title
        self.artist = artist

    def render(self):
        pass


class Game(nygame.Game):
    def __init__(self):
        super().__init__(fps = 120, showfps = True)

    def loop(self, events):
        pass


Game().run()
