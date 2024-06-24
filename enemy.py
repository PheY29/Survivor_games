import pygame
import random
import math

from pygame.math import Vector2 as vector
from sprite import BorderSprite, CollidableSprite
from projectile import Bullet
from item import Item


class EnemySpawner:
    def __init__(self, game, group, spawn_dic):
        self.game = game
        self.spawn = spawn_dic
        self.all_sprites = group
        self.enemy_group = pygame.sprite.Group()
        self.monster_sprites = self.import_monster_sprites()

        # monster stats
        self.monsters_base_stats = {
            "base_health": lambda: random.randint(5, 10),
            "base_attack": lambda: random.randint(1, 2),
            "base_defense": 0,
            "base_experience_given": lambda: round(random.uniform(1 + self.game.actual_round/5,
                                                                  2 + self.game.actual_round/5))
        }

        self.total_spawned_monster = 0
        self.total_killed_monster = 0

    def update(self):
        pass

    def import_monster_sprites(self):
        img_dict = {"mushroom": [],
                    "golem": [],
                    "goblin": []
                    }
        width, height = 64, 64
        nb_of_sprite = 4
        sprite_sheet = pygame.image.load("assets/sprite/enemy/enemy_sprite.png").convert_alpha()

        monsters = ["mushroom", "golem", "goblin"]

        for row, monster in enumerate(monsters):
            for col in range(nb_of_sprite):
                sprite = sprite_sheet.subsurface(pygame.Rect(col * width, row * height, width, height))
                img_dict[monster].append(sprite)

        return img_dict

    def spawn_enemy(self, round_lvl):
        # select a random spawn and write his infos
        spawn_names = list(self.spawn.keys())
        random_spawn_name = random.choice(spawn_names)
        random_spawn_info = self.spawn[random_spawn_name]
        random_x = random.uniform(random_spawn_info['x'], random_spawn_info['x'] + random_spawn_info['width'])
        random_y = random.uniform(random_spawn_info['y'], random_spawn_info['y'] + random_spawn_info['height'])

        # select type of enemy
        if round_lvl <= 5:
            enemy_type = "classic"
        elif 6 <= round_lvl <= 10:
            enemy_type = random.choices(["classic", "stupid"], weights=[80, 20])[0]
        else:
            enemy_type = random.choices(["classic", "stupid", "smart"], weights=[50, 30, 20])[0]

        # select sprites depending on the type
        if enemy_type == "classic":
            enemy_sprites = self.monster_sprites["mushroom"]
        elif enemy_type == "stupid":
            enemy_sprites = self.monster_sprites["golem"]
        else:
            enemy_sprites = self.monster_sprites["goblin"]

        new_enemy = Enemy(self.game, random_x, random_y, self,
                          self.monsters_base_stats, enemy_type, self.enemy_group, enemy_sprites)

        self.total_spawned_monster += 1
        self.enemy_group.add(new_enemy)
        self.all_sprites.add(new_enemy)

        if self.game.actual_round != self.game.previous_round:
            self.enemy_growing(round_lvl)

    def enemy_growing(self, round_lvl):
        for enemy in self.enemy_group:
            if not enemy.stats_upgraded:
                enemy.health = int(enemy.base_health/2 + (enemy.base_health/2 * round_lvl))
                enemy.attack = int(enemy.base_attack/2 + (enemy.base_attack/2 * round_lvl))
                enemy.defense = int(enemy.base_defense + (0.5 * round_lvl))
                enemy.stats_upgraded = True


class Enemy(pygame.sprite.Sprite):
    def __init__(self, game, x, y, spawner, monster_stats, enemy_type, enemy_group, sprites):
        super().__init__()
        self.game = game
        self.spawner = spawner
        self.monster_stats = monster_stats
        self.enemy_group = enemy_group

        self.sprites = sprites
        self.image = self.sprites[0].convert_alpha()
        self.rect = self.image.get_frect(topleft=(x, y))
        self.hitbox = self.rect.inflate(-self.rect.width / 2, -20)

        self.mask = pygame.mask.from_surface(self.image)
        self.draw_mask = self.mask.to_surface()
        self.drawing_order = self.game.layer_drawing_order["main"]

        # animation
        self.animation_index = 0
        self.animation_speed = 0.05
        self.facing_right = True

        # other
        self.direction = vector()
        self.speed = 2 if self.game.scaling == 3 else 3
        self.repulsion = 1.5
        self.stats_upgraded = False
        self.enemy_type = enemy_type
        self.random_movement_timer = 0

        self.enemy_bullets_group = pygame.sprite.Group()
        self.shooting_power = True if enemy_type == "smart" else False
        self.shooting_cooldown = 0

        # base_stats
        self.base_health = self.monster_stats["base_health"]()
        self.base_attack = self.monster_stats["base_attack"]()
        self.base_defense = self.monster_stats["base_defense"]
        self.base_experience_given = self.monster_stats["base_experience_given"]()

        # stats
        self.health = self.base_health
        self.attack = self.base_attack
        self.defense = self.base_defense
        self.experience_given = self.base_experience_given

    def update(self):
        self.draw_mask = self.mask.to_surface()

        self.follow_player()
        self.collide_player()
        self.dodge_obstacles()
        self.dodge_other_enemies()
        self.move()
        self.check_bullet_collision()
        self.animate()

    def follow_player(self):
        player_pos = vector(self.game.player.rect.center)
        enemy_pos = vector(self.rect.center)
        dist = enemy_pos.distance_to(player_pos)

        try:
            # classic = rush on player everywhere
            # smart = follow player but stay dist > 300
            # stupid = random mouvement and if dist < 300 rush player
            if self.enemy_type == "classic":
                self.direction = (player_pos - enemy_pos).normalize()

            elif self.enemy_type == "smart" and self.shooting_power:
                if dist > 300:
                    self.direction = (player_pos - enemy_pos).normalize()
                else:
                    if self.random_movement_timer <= 0:
                        self.random_movement_timer = 300
                        self.direction = vector(random.uniform(-1, 1), random.uniform(-1, 1)).normalize()
                    else:
                        self.random_movement_timer -= 1

                    if dist <= 50:
                        self.direction *= -1

                    if self.rect.centerx < self.game.player.rect.centerx:
                        right_dir = True
                    else:
                        right_dir = False

                    self.is_shooting(right_dir)

            elif self.enemy_type == "stupid":
                if dist <= 300:
                    self.direction = (player_pos - enemy_pos).normalize()
                else:
                    if self.random_movement_timer <= 0:
                        self.random_movement_timer = 300
                        self.direction = vector(random.uniform(-1, 1), random.uniform(-1, 1)).normalize()
                    else:
                        self.random_movement_timer -= 1

        except ValueError:
            pass

    def collide_player(self):
        if pygame.sprite.collide_mask(self, self.game.player):
            if self.hitbox.right > self.game.player.hitbox.left and self.direction.x > 0:
                self.direction.x = 0
            if self.hitbox.left < self.game.player.hitbox.right and self.direction.x < 0:
                self.direction.x = 0
            if self.hitbox.bottom > self.game.player.hitbox.top and self.direction.y > 0:
                self.direction.y = 0
            if self.hitbox.top < self.game.player.hitbox.bottom and self.direction.y < 0:
                self.direction.y = 0

            self.game.player.damage(self.attack)

    def dodge_obstacles(self):
        border_actions = {
            # set self.hitbox.left = obstacle.hitbox.right  for "left" etc
            "left": lambda obstacle: setattr(self.hitbox, "left", obstacle.hitbox.right),
            "right": lambda obstacle: setattr(self.hitbox, "right", obstacle.hitbox.left),
            "top": lambda obstacle: setattr(self.hitbox, "top", obstacle.hitbox.bottom),
            "bottom": lambda obstacle: setattr(self.hitbox, "bottom", obstacle.hitbox.top)
        }

        for sprite in self.game.collision_sprites:
            if isinstance(sprite, BorderSprite):
                if self.hitbox.colliderect(sprite.hitbox):
                    border = sprite.properties.get("border")
                    if border in border_actions:
                        border_actions[border](sprite)

                        if border == "left":
                            self.rect.left = self.hitbox.left
                        elif border == "right":
                            self.rect.right = self.hitbox.right
                        elif border == "top":
                            self.rect.top = self.hitbox.top
                        elif border == "bottom":
                            self.rect.bottom = self.hitbox.bottom

            if self.hitbox.colliderect(sprite.hitbox):
                obstacle_pos = vector(sprite.hitbox.center)
                enemy_pos = vector(self.hitbox.center)
                dodge_direction = (enemy_pos - obstacle_pos).normalize()
                self.direction += dodge_direction * self.repulsion

    def dodge_other_enemies(self):
        for enemy in self.enemy_group:
            if enemy != self and self.hitbox.colliderect(enemy.hitbox):
                self.collision_with_enemy(enemy)

    def collision_with_enemy(self, other_enemy):
        if self.hitbox.colliderect(other_enemy.hitbox):
            self_pos = vector(self.hitbox.center)
            other_pos = vector(other_enemy.hitbox.center)
            dodge_direction = (self_pos - other_pos).normalize()

            self.direction += dodge_direction * self.repulsion
            other_enemy.direction -= dodge_direction * self.repulsion

    def move(self):
        if self.direction.length() > 0:
            self.direction = self.direction.normalize()

            self.facing_right = True if self.direction.x > 0 else False

        self.rect.center += self.direction * self.speed
        self.hitbox.center = self.rect.center

    def check_bullet_collision(self):
        for sprite in self.game.collision_sprites.sprites():
            if isinstance(sprite, CollidableSprite):
                for bullet in self.enemy_bullets_group:
                    if pygame.sprite.collide_mask(bullet, sprite):
                        bullet.in_collision = True

        for bullet in self.enemy_bullets_group:
            if pygame.sprite.collide_mask(bullet, self.game.player):
                bullet.in_collision = True
                self.game.player.damage(self.attack)

    def is_shooting(self, direction):
        if self.shooting_cooldown == 0:
            self.shooting_cooldown = 50
            self.bullet = Bullet(self.rect.centerx, self.rect.centery, self.obtain_player_angle(),
                                 self.game.scaling, 7, self.drawing_order, direction, "spear")
            self.game.all_sprites.add(self.bullet)
            self.enemy_bullets_group.add(self.bullet)
        else:
            self.shooting_cooldown -= 1

    def obtain_player_angle(self):
        player_pos = self.game.player.hitbox.center
        dist_x = player_pos[0] - self.rect.centerx
        dist_y = player_pos[1] - self.rect.centery
        return math.atan2(dist_y, dist_x)

    def damage(self, amount):
        damage = 0 if amount <= (self.defense/2) else (amount - self.defense/2)
        self.health -= damage

        if self.health <= 0:
            self.spawner.total_killed_monster += 1
            self.game.player.experience += self.experience_given
            self.game.player.total_experience += self.experience_given
            self.kill()
            self.drop_item(self.rect.center)

    def drop_item(self, pos):
        roll = random.randint(0, 100)
        if roll >= 75:
            self.item = Item(self.game, pos)

    def animate(self):
        if self.direction.length() != 0:
            self.animation_index += self.animation_speed
            if self.animation_index >= len(self.sprites):
                self.animation_index = 0

            self.image = self.sprites[int(self.animation_index)]
            if not self.facing_right:
                self.image = pygame.transform.flip(self.image, True, False)

        self.mask = pygame.mask.from_surface(self.image)
