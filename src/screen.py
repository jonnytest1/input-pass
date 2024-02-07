from typing import Optional, Sequence, Union
import pygame
import os
import time
import sys
import pygame.display
import debugpy
from dataclasses import dataclass

from convertable_screen import ConvertableScreen

print('begin')
print(pygame.init())
pygame.display.init()


@dataclass
class TextDsp:
    text: str
    pos: Sequence[float]


def start_screen():
    try:
        while (pygame.display.get_driver() == "offscreen"):
            time.sleep(1)

        desktopSizes = pygame.display.get_desktop_sizes()
        print("sizes: "+str(desktopSizes))

        lcd1 = ConvertableScreen(pygame.display.set_mode(
            desktopSizes[0], pygame.FULLSCREEN, display=0))
        origblit = lcd1.blit

        def blit2(source: pygame.surface.Surface, dest: Sequence[float]):
            return origblit(source, dest)
        lcd1.blit = blit2  # type: ignore

        def draw():
            pygame.display.update()

        width = desktopSizes[0][1]

        lcd1.fill(pygame.Color('yellow'))
        draw()
        font = pygame.font.SysFont(None, 24)
        running = 0

        background = pygame.Color('yellow')

        texts = [TextDsp("", (20, 20)), TextDsp("", (20, 60))]
        stopped = False
        while not stopped:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    print("Mouse button pressed")
                if event.type == pygame.FINGERDOWN:
                    background = pygame.Color('orange')
                    texts[1].text = f'x:{event.x}  y:{event.y}'
                    print("Finger touched the screen")
                if event.type == pygame.QUIT:
                    running = 0
            lcd1.fill(background)
            texts[0].text = str(running)
            for text in texts:
                img = font.render(text.text, True, pygame.Color('black'))
                lcd1.blit(img, text.pos)

            draw()
            running += 1
            time.sleep(0.1)
        print("stopped ui thread")
    except Exception as e:
        print("exception in ui thread", e)
        pass
