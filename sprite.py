import pygame
from pygame.math import Vector2 as vector

layer_drawing_order = {
            "bg": 0,
            "main": 1,
            "fg": 2
        }


class Sprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups, drawing_order=layer_drawing_order["main"]):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(topleft=pos)
        self.hitbox = self.rect.copy()
        self.drawing_order = drawing_order

        self.mask = pygame.mask.from_surface(self.image)
        self.draw_mask = self.mask.to_surface()


class BorderSprite(Sprite):
    def __init__(self, pos, surf, groups, properties):
        super().__init__(pos, surf, groups)
        self.hitbox = self.rect.copy()
        self.properties = properties


class CollidableSprite(Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(pos, surf, groups)
        self.hitbox = self.rect.copy()


class AllSprite(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.screen = pygame.display.get_surface()
        self.offset = vector()

    # Basic camera
    # def draw(self, player_center, map_width, map_height):
    #     # center the camero on the player
    #     self.offset.x = -(player_center[0] - self.screen.get_width() // 2)
    #     self.offset.y = -(player_center[1] - self.screen.get_height() // 2)
    #
    #     for sprite in self:
    #         self.screen.blit(sprite.image, sprite.rect.topleft + self.offset)

    # Upgraded camera
    def draw(self, player_center, map_width=int, map_height=int):
        # Center the camera on the player
        self.offset.x = -(player_center[0] - self.screen.get_width() // 2)
        self.offset.y = -(player_center[1] - self.screen.get_height() // 2)

        # Limit the camera movement to stay within the map edge
        self.offset.x = min(0, max(self.offset.x, -(map_width - self.screen.get_width())))
        self.offset.y = min(0, max(self.offset.y, -(map_height - self.screen.get_height())))

        bg_sprites = [sprite for sprite in self if sprite.drawing_order < layer_drawing_order["main"]]
        main_sprites = sorted([sprite for sprite in self if sprite.drawing_order == layer_drawing_order["main"]],
                              key=lambda sprite: sprite.rect.centery)
        fg_sprites = [sprite for sprite in self if sprite.drawing_order > layer_drawing_order["main"]]

        # tuple with order you need
        for layer in (bg_sprites, main_sprites, fg_sprites):
            for sprite in layer:
                self.screen.blit(sprite.image, sprite.rect.topleft + self.offset)
