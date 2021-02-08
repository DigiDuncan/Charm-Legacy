import pygame
from charm.lib import nygame
from charm.lib.display import display


class Game():
    def __init__(self):
        self.running = True
        self.size = (800, 600)
        self.clock = nygame.time.Clock()

        self.screen = display.add_layer(pygame.Surface(self.size))

    def run(self):
        pygame.init()

        display.set_mode(self.size)

        while self.running:
            # Window close button
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False

            # Final draw stage
            display.flip()
            # Timing loop
            self.clock.tick_busy_loop(60)


def main():
    g = Game()
    g.run()


# This is needed, or else calling `python -m <name>` will mean that main() is called twice.
if __name__ == "__main__":
    main()
