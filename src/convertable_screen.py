from typing import Sequence
import pygame
from pygame.surface import Surface


class ConvertableScreen:

    def __init__(self, surface: Surface):
        self.surface = surface
        size = surface.get_size()
        self.width = size[0]
        self.height = size[0]

    def blit(self, source: Surface, dest: Sequence[float]):

        new_dest = (self.height-dest[1], dest[0])
        rotate90 = pygame.transform.rotate(source, -90)
        self.surface.blit(rotate90, new_dest)
        pass

    def fill(self, col):
        self.surface.fill(col)
