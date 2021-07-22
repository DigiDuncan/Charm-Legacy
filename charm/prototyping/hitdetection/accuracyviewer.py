import pygame.image
from pygame.surface import Surface
import pygame.transform


class AccuracyViewer:
    def __init__(self, size = (200, 50)) -> None:
        self.size = size
        self.imagefolder = R".\\charm\\data\\images\\judgements\\"
        self.judgementnames = ["supercharming", "charming", "excellent", "great", "good", "ok", "miss"]
        self.offsets = [0.01, 0.025, 0.035, 0.045, 0.06, 0.07]
        self.image = Surface(self.size)

        self.judgements = {k: pygame.image.load(self.imagefolder + k + ".png") for k in self.judgementnames}
        for k, v in self.judgements.items():
            iw = v.get_width()
            ih = v.get_height()
            sh = self.size[1]
            r = ih / sh
            w = int(iw / r)
            self.judgements[k] = pygame.transform.smoothscale(v, (w, sh))

    def get_judgement_name(self, offset):
        index = 0
        offset = abs(offset)
        for o in self.offsets:
            if o >= offset:
                return self.judgementnames[index]
            else:
                index += 1
        return self.judgementnames[-1]

    def hit(self, offset):
        self.image.fill((0, 0, 0, 0))
        sprite = self.judgements[self.get_judgement_name(offset)]
        rect = sprite.get_rect()
        rect.center = self.image.get_rect().center
        self.image.blit(sprite, rect)

    def miss(self):
        self.image.fill((0, 0, 0, 0))
        sprite = self.judgements["miss"]
        rect = sprite.get_rect()
        rect.center = self.image.get_rect().center
        self.image.blit(sprite, rect)
