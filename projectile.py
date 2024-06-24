import pygame
import math


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle, scaling, bullet_speed, drawing_order, direction, projectile_type):
        super().__init__()
        self.sprites = self.import_projectile_sprite()[projectile_type]
        self.image = self.sprites["normal"][0]
        self.rect = self.image.get_frect(center=(x, y))
        self.mask = pygame.mask.from_surface(self.image)
        self.draw_mask = self.mask.to_surface()

        self.drawing_order = drawing_order
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = bullet_speed

        self.x_vel = math.cos(self.angle) * self.speed
        self.y_vel = math.sin(self.angle) * self.speed

        self.bullet_life_time = 250 * scaling  # ms
        self.spawn_time = pygame.time.get_ticks()

        # Animation
        self.animation_index = 0
        self.in_collision = False
        self.collision_animation_index = 0
        self.animation_speed = 0.1
        self.direction = direction

    def move(self):
        self.x += self.x_vel
        self.y += self.y_vel

        self.rect.centerx = int(self.x)
        self.rect.centery = int(self.y)

        if pygame.time.get_ticks() - self.spawn_time > self.bullet_life_time:
            self.kill()

    def update(self):
        self.draw_mask = self.mask.to_surface()

        if not self.in_collision:
            self.move()
        self.animate()

    def animate(self):
        if not self.in_collision:
            state = "normal"
            self.animation_index += self.animation_speed
            if self.animation_index >= len(self.sprites[state]):
                self.animation_index = 0
            self.image = self.sprites[state][int(self.animation_index)]
            index = int(self.animation_index)
        else:
            state = "collision"
            self.collision_animation_index += self.animation_speed
            if self.collision_animation_index >= len(self.sprites[state]):
                self.kill()
                self.collision_animation_index = 0
            index = int(self.collision_animation_index)

        if not self.direction:
            self.image = pygame.transform.flip(self.image, True, False)

        self.image = pygame.transform.rotate(self.sprites[state][index], -math.degrees(self.angle))
        self.rect = self.image.get_frect(center=(self.x, self.y))
        self.mask = pygame.mask.from_surface(self.image)

    def import_projectile_sprite(self):
        img_dict = {"spear": {"normal": [], "collision": []},
                    "fire_ball": {"normal": [], "collision": []}}

        width, height = 64, 64
        nb_of_normal_sprites = 3
        nb_of_collision_sprites = 2

        sprite_sheet = pygame.image.load("assets/sprite/projectile/projectile.png").convert_alpha()

        projectiles = ["spear", "fire_ball"]

        for row, projectile in enumerate(projectiles):
            for col in range(nb_of_normal_sprites):
                sprite = sprite_sheet.subsurface(pygame.Rect(col * width, row * height, width, height))
                if projectile == "spear":
                    sprite = pygame.transform.scale_by(sprite,  1.5)
                    sprite = pygame.transform.rotate(sprite, 45)
                img_dict[projectile]["normal"].append(sprite)

            for col in range(nb_of_normal_sprites, nb_of_normal_sprites + nb_of_collision_sprites):
                sprite = sprite_sheet.subsurface(pygame.Rect(col * width, row * height, width, height))
                if projectile == "spear":
                    sprite = pygame.transform.scale_by(sprite, 1.5)
                    sprite = pygame.transform.rotate(sprite, 45)
                img_dict[projectile]["collision"].append(sprite)

        return img_dict
