import pygame
# from charm.lib import nygame


def setup():
    pygame.init()

    flags = pygame.DOUBLEBUF

    pygame.display.set_mode((800, 600), flags)


def main():
    setup()


# This is needed, or else calling `python -m <name>` will mean that main() is called twice.
if __name__ == "__main__":
    main()
