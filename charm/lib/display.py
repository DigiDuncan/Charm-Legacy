import pygame


class Display():
    __slots__ = ["layers", "output_surface", "size", "fullscreen"]

    def __init__(self):
        self.layers = []
        self.output_surface = None
        self.size = None
        self.fullscreen = None

    def set_mode(self, display_size, fullscreen=False):
        """Set the display mode

        This function will create the display window/screen at the newly requested size.

        The display_size argument is a pair of numbers representing the width and height of the window/screen output.
        The fullscreen argument is a boolean representing whether to create a window or a fullscreen display.

        In fullscreen mode, if a display_size is (0, 0), the full screen resolution will be used.

        Parameters
        ----------
        display_size : tuple
            The size of the display output the surface will be displayed on. The input layers will automatically scale to fit this.
        full_screen : bool, optional
            Whether to create a window or a fullscreen display.
        """
        flags = pygame.DOUBLEBUF
        if fullscreen:
            flags = flags | pygame.FULLSCREEN
        self.output_surface = pygame.display.set_mode(display_size, flags)
        self.size = self.output_surface.get_size()
        self.fullscreen = fullscreen

    def reset_layers(self):
        self.layers.clear()

    def add_layer(self, surface):
        self.layers.append(surface)
        return surface

    def remove_layer(self, surface):
        self.layers.remove(surface)

    def flip(self):
        """Update the full display Surface to the screen

        This will update the contents of the entire display.
        The input surface will automatically be scaled to fit the window output.
        """
        if self.output_surface is None:
            raise ValueError("Display is not initialized")
        for layer in self.layers:
            if layer.get_size() == self.size:
                # If layer is the same size as the output, just blit it over
                self.output_surface.blit(layer, (0, 0))
            else:
                # If layer is a different size then the output, scale it to the output
                pygame.transform.scale(layer, self.size, self.output_surface)
        pygame.display.flip()


display = Display()
