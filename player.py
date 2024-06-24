import pygame

from pygame.math import Vector2 as vector
from projectile import Bullet
from sprite import CollidableSprite
from enemy import Enemy, Item


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, game, save_stats):
        super().__init__(groups)
        self.game = game

        self.sprites = self.import_player_sprite()["player"]
        self.image = self.sprites[0]
        self.rect = self.image.get_frect(topleft=pos)
        # inflate : divide rect width by 2 and subtract top and bottom by -20
        self.hitbox = self.rect.inflate(-self.rect.width/2, -20)

        self.mask = pygame.mask.from_surface(self.image)
        self.draw_mask = self.mask.to_surface()

        self.drawing_order = self.game.layer_drawing_order["main"]
        self.starting_pos = []
        self.direction = vector()
        self.speed = 5.5 if self.game.scaling == 3 else 7

        # Animation variables
        self.animation_index = 0
        self.animation_speed = 0.1
        self.facing_right = True

        # projectile
        self.bullets_group = pygame.sprite.Group()
        self.shoot = False
        self.shooting_cooldown = 0
        self.invulnerable_duration = 500  # 0.5sec
        self.last_hit_time = 0

        # saved stats
        self.save_stats = save_stats
        # base stats
        self.base_health = 10
        self.base_attack = 4
        self.base_defense = 1
        self.base_experience = 18

        # stats
        self.death = False
        self.level = self.save_stats["level"] if self.save_stats else 1
        self.next_level = None
        self.health = self.save_stats["health"] if self.save_stats else self.base_health
        self.attack = self.save_stats["attack"] if self.save_stats else self.base_attack
        self.defense = self.save_stats["defense"] if self.save_stats else self.base_defense
        self.bullet_cd = self.save_stats["bullet_cd"] if self.save_stats else 15  # 15 = 0 -> max : 10 = 5
        self.bullet_spd = self.save_stats["bullet_spd"] if self.save_stats else 7  # max = 25
        self.experience = self.save_stats["experience"] if self.save_stats else 0
        self.total_experience = self.save_stats["total_experience"] if self.save_stats else 0

    def update(self):
        self.draw_mask = self.mask.to_surface()

        self.input()
        self.move()
        self.animate()

        if self.shooting_cooldown > 0:
            self.shooting_cooldown -= 1

        self.check_bullet_collision()

    def input(self):
        try:
            if self.game.mouse_button[0]:
                self.shoot = True

                if self.game.mouse_pos[0] > self.game.width//2:
                    right_dir = True
                else:
                    right_dir = False

                self.is_shooting(right_dir)
            else:
                self.shoot = False
        except KeyError:
            pass

        self.keys = pygame.key.get_pressed()
        input_vector = vector()

        for key, value in self.game.configurations.items():
            if isinstance(value, str):
                if self.keys[(getattr(pygame, f"K_{value}"))]:
                    if key == 'up':
                        input_vector.y -= 1
                    if key == 'down':
                        input_vector.y += 1
                    if key == 'left':
                        input_vector.x -= 1
                        self.facing_right = False
                    if key == 'right':
                        input_vector.x += 1
                        self.facing_right = True

        if input_vector[0] != 0 and input_vector[1] != 0:
            input_vector.normalize_ip()
        self.direction = input_vector

    def move(self):
        self.rect.centerx += self.direction.x * self.speed
        self.hitbox.centerx = self.rect.centerx
        self.check_collision("horizontal")

        self.rect.centery += self.direction.y * self.speed
        self.hitbox.centery = self.rect.centery
        self.check_collision("vertical")

    def check_collision(self, axe):
        for sprite in self.game.collision_sprites:
            if sprite.hitbox.colliderect(self.hitbox):
                if axe == "horizontal":
                    if self.direction.x > 0:
                        self.hitbox.right = sprite.hitbox.left
                    if self.direction.x < 0:
                        self.hitbox.left = sprite.hitbox.right
                    self.rect.centerx = self.hitbox.centerx
                else:
                    if self.direction.y > 0:
                        self.hitbox.bottom = sprite.hitbox.top
                    if self.direction.y < 0:
                        self.hitbox.top = sprite.hitbox.bottom
                    self.rect.centery = self.hitbox.centery

        for sprite in self.game.all_sprites:
            if isinstance(sprite, Item):
                if sprite.hitbox.colliderect(self.hitbox):
                    self.health = min(self.base_health, self.health+3)
                    sprite.kill()

    def check_bullet_collision(self):
        # only collision_obj (stone and trunk) for bullets
        for sprite in self.game.collision_sprites.sprites():
            if isinstance(sprite, CollidableSprite):
                for bullet in self.bullets_group:
                    if pygame.sprite.collide_mask(bullet, sprite):
                        bullet.in_collision = True

        # Collision entre les balles et les ennemis
        for sprite in self.game.all_sprites.sprites():
            if isinstance(sprite, Enemy):
                for bullet in self.bullets_group:
                    if pygame.sprite.collide_mask(bullet, sprite):
                        if not bullet.in_collision:
                            sprite.damage(self.attack)
                        bullet.in_collision = True

    def is_shooting(self, direction):
        if self.shooting_cooldown == 0 and self.shoot:
            self.shooting_cooldown = int(self.bullet_cd)
            self.bullet = Bullet(self.hitbox.centerx, self.hitbox.centery+10, self.game.get_mouse_angle(),
                                 self.game.scaling, self.bullet_spd, self.drawing_order, direction, "fire_ball")
            self.game.all_sprites.add(self.bullet)
            self.bullets_group.add(self.bullet)

    def level_up(self):
        remain_exp = (self.experience - self.next_level) if self.experience > self.next_level else 0
        self.experience = 0 + remain_exp
        self.level += 1
        self.base_health += 5
        self.health += 5
        self.attack += 1.5
        self.defense += 0.5

    def damage(self, amount):
        current_time = pygame.time.get_ticks()

        if current_time - self.last_hit_time >= self.invulnerable_duration:
            if self.health > 0:
                self.health -= (amount - self.defense / 2)
                if self.health <= 0:
                    self.health = 0
            else:
                self.health = 0
            self.last_hit_time = current_time

    def import_player_sprite(self):
        img_dict = {}
        width, height = 64, 64
        nb_of_sprite = 4

        sprite_sheet = pygame.image.load("assets/sprite/player/player_sprite.png").convert_alpha()
        sprites = []

        for i in range(nb_of_sprite):
            sprite = sprite_sheet.subsurface(pygame.Rect(i * width, 0, width, height))
            sprites.append(sprite)

        img_dict["player"] = sprites
        return img_dict

    def animate(self):
        if self.direction.length() != 0:  # If the player is moving
            self.animation_index += self.animation_speed
            if self.animation_index >= len(self.sprites):
                self.animation_index = 0

            self.image = self.sprites[int(self.animation_index)]
            if not self.facing_right:
                self.image = pygame.transform.flip(self.image, True, False)

        self.mask = pygame.mask.from_surface(self.image)
