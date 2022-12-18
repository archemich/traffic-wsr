import argparse
import copy
import logging
from pathlib import Path
from math import floor
import numpy as np

import pygame as pg
import pygame.transform

from .version import __version__


def parse_args() -> argparse.Namespace:

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--version',
                        action='version',
                        version=__version__)
    parser.add_argument('--log-level', )
    args = parser.parse_args()
    return args


class Car(pg.sprite.Sprite):
    def __init__(self, image):
        pg.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect()

class Road(pg.sprite.Sprite):
    def __init__(self, image):
        pg.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect()


class Game:

    width: int
    height: int
    width_cells: int
    height_cells: int
    cells: np.ndarray
    fps: int
    assets_path: Path
    map_rect: pg.Rect
    list_width_cells: int = 5  # cells
    list_rect: pg.Rect
    cell_size = 30  # px

    def __init__(self,
                 width_cells,
                 height_cells,
                 fps,
                 assets_path: Path):
        Game.width_cells = width_cells
        Game.height_cells = height_cells
        Game.cells = np.full((height_cells, width_cells), [])
        Game.width = width_cells * Game.cell_size
        Game.height = height_cells * Game.cell_size
        width = Game.width
        height = Game.height
        Game.fps = fps
        Game.assets_path = assets_path

        self.drag = None
        self.to_delete = None

        pg.init()
        self.screen = pg.display.set_mode((width, height))
        self.background = (255, 255, 255)
        self.screen.fill(self.background)
        pg.display.set_caption("My Game")
        self.clock = pg.time.Clock()

        self.sprites_img = self._load_sprites(assets_path)

        self.all_sprites = pg.sprite.Group()
        self.static_sprites = pg.sprite.Group()
        self.dynamic_sprites = pg.sprite.Group()

        car = Car(self.sprites_img['car_red'])
        road = Road(self.sprites_img['road'])

        self.static_sprites.add(car)
        self.static_sprites.add(road)

        self.all_sprites.add(self.static_sprites.sprites())
        self.all_sprites.add(self.dynamic_sprites.sprites())

        # First render
        self._init_ui()
        self.all_sprites.draw(self.screen)
        pg.display.flip()

    def run(self):
        running = True

        while running:
            delta = self.clock.tick(self.fps)

            # Handle events
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                self._handle_lmb(event)
                self._handle_rmb(event)
                self._handle_keyboard(event)

            # Handle logic
            self.all_sprites.update()

            # Rendering
            self.screen.fill(self.background)
            self.all_sprites.draw(self.screen)
            self._draw_ui()
            pg.display.flip()

        pg.quit()

    def _handle_lmb(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                def drag(sprite, mouse):
                    mouse_x, mouse_y = mouse
                    rect = sprite.rect
                    self.drag = {
                        'sprite': sprite,
                        'offset': {
                            'x': rect.x - mouse_x,
                            'y': rect.y - mouse_y
                        }
                    }

                for sprite in self.static_sprites:
                    if sprite.rect.collidepoint(event.pos):
                        cp = self._dup_sprite(sprite)
                        self.all_sprites.add(cp)
                        self.dynamic_sprites.add(cp)
                        drag(cp, event.pos)

                for sprite in self.dynamic_sprites:
                    if sprite.rect.collidepoint(event.pos):
                        drag(sprite, event.pos)

        elif event.type == pg.MOUSEBUTTONUP:
            if event.button == 1:
                mouse_x, mouse_y = event.pos
                rect = self.drag['sprite'].rect
                cell_x, cell_y = self._get_cell_by_pos(mouse_x, mouse_y)
                rect.x = cell_x * self.cell_size
                rect.y = cell_y * self.cell_size
                self.cells[cell_y][cell_x].append(self.drag['sprite'])
                self.drag = None

        elif event.type == pg.MOUSEMOTION:
            if self.drag:
                mouse_x, mouse_y = event.pos
                rect = self.drag['sprite'].rect
                rect.x = mouse_x + self.drag['offset']['x']
                rect.y = mouse_y + self.drag['offset']['y']

    def _handle_rmb(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 3:
                for sprite in self.dynamic_sprites:
                    if sprite.rect.collidepoint(event.pos):
                        self.to_delete = sprite
        elif event.type == pg.MOUSEBUTTONUP:
            if event.button == 3:
                if self.to_delete:
                    if self.to_delete.rect.collidepoint(event.pos):
                        self.dynamic_sprites.remove(self.to_delete)
                        self.all_sprites.remove(self.to_delete)
                        self.to_delete = None

    def _handle_keyboard(self, event):
        if event.type == pg.KEYDOWN:
            if event.scancode == 21:
                for sprite in self.dynamic_sprites:
                    if sprite.rect.collidepoint(pygame.mouse.get_pos()):
                        rot = -90
                        # if left shift pressed rotate anti-clockwise
                        if event.mod == 1:
                            rot = 90
                        sprite.image = pygame.transform.rotate(sprite.image,
                                                               rot)

    @staticmethod
    def _load_sprites(assets_path: Path):
        sprites = {}
        spr_p = assets_path / 'sprites'
        sprites.update({'car_red': pg.image.load(spr_p / 'Cvertical.png').convert()})
        sprites.update({'road': pg.image.load(spr_p / 'Rvertical.png').convert()})
        return sprites

    @staticmethod
    def _dup_sprite(sprite):
        cp = copy.copy(sprite)
        cp.rect = sprite.rect.copy()
        return cp

    def _init_ui(self):
        self.map_width = self.width - (self.list_width_cells * self.cell_size)
        self.map_rect = pg.Rect(0, 0, self.map_width, self.height)
        self.list_rect = pg.Rect(self.map_width, 0,
                                 self.width - self.map_width, self.height)

        for i, spr in enumerate(self.static_sprites):
            offset = self.cell_size + 12
            y = self.cell_size / 2
            spr.rect.center = ((self.map_width + self.width) / 2, y + offset * i)

    def _draw_ui(self):
        pg.draw.line(self.screen, (0, 0, 0), (self.map_width, 0),
                     (self.map_width, self.height))

    def _get_cell_by_pos(self, x, y):
        """Get x,y of cell in pos."""
        return x // self.cell_size, y // self.cell_size


def main():
    """
    Script entry point
    """

    args = parse_args()

    game = Game(20, 20, 60, Path(__file__).parent / 'resources')
    game.run()


if __name__ == '__main__':
    main()
