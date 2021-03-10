import pygame
import pygame.freetype
from itertools import cycle


def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    data = cycle(['This is an example.', 'This is another, longer sentence.'])

    font = pygame.freetype.Font(None, 50)

    font.origin = True
    current = ""
    last_ticks = -1000
    idx = 0

    while True:
        events = pygame.event.get()
        for e in events:
            if e.type == pygame.QUIT:
                return

        now = pygame.time.get_ticks()
        if last_ticks + 500 < now:
            last_ticks = now
            # if we press the correct letter, move the index
            idx += 1
            if idx >= len(current):
                print("OHNO")
                # if the sentence is complete, let's prepare the
                # next surface
                idx = 0
                current = next(data)
                text_surf_rect = font.get_rect(current)
                baseline = text_surf_rect.y
                text_surf = pygame.Surface(text_surf_rect.size)
                text_surf_rect.center = screen.get_rect().center

        # clear everything
        screen.fill('white')
        text_surf.fill('white')

        dest = (0, baseline)
        # render each letter of the current sentence one by one
        before = current[:idx]
        dest = draw_text(text_surf, dest, before, 'lightgrey', font)
        letter = current[idx]
        dest = draw_text(text_surf, dest, letter, 'lightblue', font)
        after = current[idx + 1:]
        dest = draw_text(text_surf, dest, after, 'black', font)

        screen.blit(text_surf, text_surf_rect)
        pygame.display.flip()
        clock.tick(30)


def draw_text(surf, dest, text, color, font):
    font.render_to(surf, dest, text, color)
    metrics = font.get_metrics(text)
    HORIZONTAL_ADVANCE_X = 4
    adv_x = sum(m[HORIZONTAL_ADVANCE_X] for m in metrics)
    new_dest = (dest[0] + adv_x, dest[1])
    return new_dest


if __name__ == '__main__':
    main()
