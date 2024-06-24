import pygame
import random


class Item(pygame.sprite.Sprite):
    def __init__(self, game, pos):
        super().__init__()
        self.game = game
        self.pos = pos
        self.image = pygame.Surface((10, 10)) if self.game.scaling == 3 else pygame.Surface((14, 14))
        self.image.fill("green")
        self.rect = self.image.get_frect(center=pos)
        self.hitbox = self.rect
        self.drawing_order = self.game.layer_drawing_order["main"]
        self.game.all_sprites.add(self)
