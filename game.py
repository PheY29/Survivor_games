import pygame
import random
import pytmx
import json
import math

from sprite import Sprite, AllSprite, BorderSprite, CollidableSprite
from player import Player
from enemy import EnemySpawner, Enemy
from item import Item


class Game:
    def __init__(self, screen, game_state_manager, color_manager):
        self.screen = screen
        self.width = self.screen.get_width()
        self.height = self.screen.get_height()
        self.game_state_manager = game_state_manager
        self.color_manager = color_manager

        # font, background
        self.font = pygame.font.Font("assets/font.ttf", size=30)
        self.rgb_color = random.randint(0, 90), random.randint(0, 90), random.randint(0, 90)

        # keyboard setup
        self.configurations = None  # used in self.import_config()
        self.keys = {}
        self.mouse_button = {}
        self.mouse_pos = ()
        self.mouse_angle = None
        self.pause = False
        self.import_config()

        # groups
        self.all_sprites = AllSprite()
        self.collision_sprites = pygame.sprite.Group()

        # game setup
        self.temporary_save = {}
        self.save_file = "others/save.json"
        self.player_stats_saved = {}
        self.previous_round = 1
        self.actual_round = 1
        self.round_menu = False
        self.base_time_per_round = 20
        self.time_per_round = int(round(self.base_time_per_round +
                                        (self.base_time_per_round * (self.actual_round * 0.15)), -1))
        self.time_before_next_round = None
        self.wave_mob_time = 10  # sec
        self.min_nb_of_monsters = 4
        self.max_nb_of_monsters = 7
        self.actual_spawn_time = None
        self.last_spawn_time = -1
        self.spawn_times = []
        self.nb_of_mob = None

        # timer
        self.actual_time = None
        self.previous_time = None
        self.pause_start_time = 0
        self.paused_time = 0

        # spawn management
        self.spawn_point = {}
        self.enemy_spawner = EnemySpawner(self, self.all_sprites, self.spawn_point)
        self.spawn_pause_start_time = 0
        self.spawn_paused_time = 0

        # map setup
        self.load_setup = False
        self.tile_size = 16
        self.new_tile_size = 64
        self.scaling = 4
        self.import_assets()
        self.layer_drawing_order = {
            "bg": 0,
            "main": 1,
            "fg": 2
        }

    def run(self):
        if not self.pause:
            if not self.load_setup:
                self.start_time = pygame.time.get_ticks()
                self.check_map_size(self.tmx_maps["world"])
                self.setup(self.tmx_maps["world"], "player_spawn")
                self.load_setup = True

            self.handle_input()
            self.check_game_state()
            self.draw_background()
            self.spawn_timer()
            self.all_sprites.update()
            self.enemy_spawner.enemy_group.update()
            self.all_sprites.draw(self.player.rect.center, self.map_width, self.map_height)
            self.front_drawings()

    def handle_input(self):
        for key, value in self.configurations.items():
            if isinstance(value, str):
                if self.keys.get(getattr(pygame, f"K_{value}")):
                    if key == 'escape':
                        self.keys = {}
                        self.pause = True
                        self.game_state_manager.set_state("pause")

    def check_game_state(self):
        if self.player.health <= 0:
            self.player.death = True
            self.delete_save()
            self.clearing_sprites_group()
            self.clearing_enemy_and_item()
            pygame.display.update()
            self.game_state_manager.set_state("death_menu")

        if self.game_state_manager.get_previous_state() == "round_menu" and self.round_menu:
            self.next_round()

        if self.player.level == 1:
            self.player.next_level = 18
        else:
            self.player.next_level = int(round((self.player.base_experience * ((self.player.level ** 2) / 2)),
                                               ndigits=1))

        if self.player.experience >= self.player.next_level:
            self.player.level_up()

        if self.time_before_next_round == 0:
            self.keys = {}
            self.mouse_button = {}
            self.mouse_pos = ()
            self.round_menu = True
            self.game_state_manager.set_state("round_menu")

    def front_drawings(self):
        if not self.player.death:
            self.drawing_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

            self.draw_stats(self.drawing_surface)
            self.draw_timer(self.drawing_surface)
            self.screen.blit(self.drawing_surface, (0, 0))

    def draw_stats(self, surface):
        # stats
        stats_to_draw = {
            "round": self.actual_round,
            "lvl": self.player.level,
            "next_lvl": int(round((self.player.base_experience * ((self.player.level ** 2) / 2)),
                                  ndigits=1)) if self.player.level > 1 else self.player.base_experience,
            "hp": self.player.health,
            "atk": self.player.attack,
            "def": self.player.defense,
            "bullet cd": self.player.bullet_cd,
            "bullet spd": self.player.bullet_spd
        }

        stats_surface_width = 40 * self.scaling + 65
        stats_surface_height = 80 * self.scaling
        pygame.draw.rect(surface, (128, 128, 128, 128),
                         (10, self.height // 2 - stats_surface_height // 2, stats_surface_width, stats_surface_height))

        font_for_stats = pygame.font.Font("assets/font.ttf", size=6 * self.scaling)
        for i, (keys, value) in enumerate(stats_to_draw.items()):
            color_for_stats = "black"
            base_y = (self.height // 2 - stats_surface_height // 2) + i * 9 * self.scaling

            if keys == "round":
                color_for_stats = "red3"

            if keys == "lvl":
                base_y += 10

            if keys == "next_lvl":
                base_y += 10
                max_width = stats_surface_width - 20
                current_experience = self.player.experience
                next_lvl_experience = stats_to_draw["next_lvl"]
                progress_exp = max(0, min(max_width, (current_experience / next_lvl_experience) * max_width))
                # min : if % obtain >= max_width, progress_width will stop at max_width
                # max : if % obtain < 0, progress_width will always be at 0

                pygame.draw.rect(surface, "grey25", (20, base_y, max_width, 20))
                pygame.draw.rect(surface, "orangered", (20, base_y, progress_exp, 20))

                font_for_exp = pygame.font.Font("assets/font.ttf", size=12)
                stats_text = font_for_exp.render(f"{current_experience}/{next_lvl_experience}",
                                                 True, "white")
                surface.blit(stats_text, ((20 + stats_surface_width) // 2 - stats_text.get_width() // 2,
                                          (base_y + 20 - stats_text.get_height())))

            elif keys == "hp":
                base_y += 10
                max_width = stats_surface_width - 20
                max_hp = self.player.base_health
                current_hp = self.player.health
                progress_hp = max(0, min(max_width, (current_hp / max_hp) * max_width))

                pygame.draw.rect(surface, "grey25", (20, base_y, max_width, 30))
                pygame.draw.rect(surface, "red", (20, base_y, progress_hp, 30))

                font_for_hp = pygame.font.Font("assets/font.ttf", size=15)
                stats_text = font_for_hp.render(f"{keys.capitalize()}: {current_hp}/{max_hp}",
                                                True, color_for_stats)
                surface.blit(stats_text, ((20 + stats_surface_width) // 2 - stats_text.get_width() // 2,
                                          (base_y + 25 - stats_text.get_height())))

            else:
                if keys in ["atk", "def", "bullet cd", "bullet spd"]:
                    base_y += 15

                stats_text = font_for_stats.render(f"{keys.capitalize()}: {value}", True, color_for_stats)
                surface.blit(stats_text, ((20 + stats_surface_width) // 2 - stats_text.get_width() // 2, base_y))

    def draw_timer(self, surface):
        # timer
        if self.pause:
            if self.pause_start_time == 0:
                self.pause_start_time = pygame.time.get_ticks()
        else:
            if self.pause_start_time != 0:
                self.paused_time += pygame.time.get_ticks() - self.pause_start_time
                self.pause_start_time = 0

        self.actual_time = (pygame.time.get_ticks() - self.start_time - self.paused_time) // 1000

        if self.actual_time != self.previous_time:
            self.previous_time = self.actual_time

        self.time_before_next_round = self.time_per_round - self.actual_time
        minutes = (self.time_per_round - self.actual_time) // 60
        seconds = (self.time_per_round - self.actual_time) % 60
        time_text = self.font.render(f"{minutes:02}:{seconds:02}", True, "orangered2")

        pygame.draw.rect(surface, (128, 128, 128, 128),
                         ((self.width // 2 - time_text.get_width() // 2), 25,
                          time_text.get_width() + 2, time_text.get_height()))
        surface.blit(time_text, ((self.width // 2 - time_text.get_width() // 2), 25))

    def spawn_timer(self):
        if not self.player.death:
            # Enemy spawner
            if self.pause:
                if self.spawn_pause_start_time == 0:
                    self.spawn_pause_start_time = pygame.time.get_ticks()
            else:
                if self.spawn_pause_start_time != 0:
                    self.spawn_paused_time += pygame.time.get_ticks() - self.spawn_pause_start_time
                    self.spawn_pause_start_time = 0

            self.actual_spawn_time = (pygame.time.get_ticks() - self.start_time - self.spawn_paused_time) // 1000

            if self.actual_spawn_time // self.wave_mob_time != self.last_spawn_time // self.wave_mob_time:
                self.last_spawn_time = self.actual_spawn_time

                if self.actual_round % 5 == 0:
                    self.min_nb_of_monsters += 1
                    self.max_nb_of_monsters += 1

                self.nb_of_mob = random.randint(self.min_nb_of_monsters, self.max_nb_of_monsters)
                self.spawn_times = [(self.last_spawn_time // self.wave_mob_time) * self.wave_mob_time +
                                    random.randint(0, 9) for _ in range(self.nb_of_mob)]
                # checks every tenth of a second example at 10sec : 10//10 = 1 * 10 = 10 + random = [13, 17, 19]

            if self.actual_spawn_time in self.spawn_times:
                self.spawn_times.remove(self.actual_spawn_time)
                self.enemy_spawner.spawn_enemy(self.actual_round)

    def draw_background(self):
        for y in range(self.height):
            interpolation = y / self.height
            color = (
                int(((1 - interpolation) * 0) + (interpolation * self.rgb_color[0])),
                int(((1 - interpolation) * 0) + (interpolation * self.rgb_color[1])),
                int(((1 - interpolation) * 0) + (interpolation * self.rgb_color[2]))
            )
            pygame.draw.line(self.screen, color, (0, y), (self.width, y))

    def get_mouse_angle(self):
        mouse_pos_on_map = (self.mouse_pos[0] - self.all_sprites.offset.x,
                            self.mouse_pos[1] - self.all_sprites.offset.y)

        dist_x = mouse_pos_on_map[0] - self.player.rect.centerx
        dist_y = mouse_pos_on_map[1] - self.player.rect.centery
        return math.atan2(dist_y, dist_x)

    def import_config(self):
        with open("others/setting.json", "r") as f:
            self.configurations = json.load(f)

    def import_assets(self):
        self.tmx_maps = {"world": pytmx.util_pygame.load_pygame("assets/map/map.tmx")}

    def check_map_size(self, tmx_map):
        self.new_tile_size = 48 if self.width == 1280 else 64
        self.scaling = 3 if self.width == 1280 else 4

        self.map_width = tmx_map.width * (self.tile_size * self.scaling)
        self.map_height = tmx_map.height * (self.tile_size * self.scaling)

    def setup(self, tmx_map, player_start_pos):
        # map and decoration
        for layer in ["map", "map_decoration", "obj_decoration"]:
            for x, y, surf in tmx_map.get_layer_by_name(layer).tiles():
                surf = pygame.transform.scale(surf, (self.new_tile_size, self.new_tile_size))
                if layer == "map":
                    Sprite((x * self.tile_size * self.scaling, y * self.tile_size * self.scaling), surf,
                           self.all_sprites, self.layer_drawing_order["bg"])
                elif layer == "map_decoration":
                    Sprite((x * self.tile_size * self.scaling, y * self.tile_size * self.scaling), surf,
                           self.all_sprites, self.layer_drawing_order["main"])
                else:
                    Sprite((x * self.tile_size * self.scaling, y * self.tile_size * self.scaling), surf,
                           self.all_sprites, self.layer_drawing_order["fg"])

        # collision border/objects
        for obj in tmx_map.get_layer_by_name("border_map"):
            BorderSprite((obj.x * self.scaling, obj.y * self.scaling),
                         pygame.Surface((obj.width * self.scaling, obj.height * self.scaling)), self.collision_sprites,
                         obj.properties)
            #  add BorderSprite to self.all_sprite to see them on the screen

        for obj in tmx_map.get_layer_by_name("collision_obj"):
            CollidableSprite((obj.x * self.scaling, obj.y * self.scaling),
                             pygame.Surface((obj.width * self.scaling, obj.height * self.scaling)),
                             self.collision_sprites)

        # enemy spawn
        for obj in tmx_map.get_layer_by_name("enemy"):
            if "enemy_spawn" in obj.name:
                self.spawn_point[obj.name] = {
                    "x": obj.x * self.scaling,
                    "y": obj.y * self.scaling,
                    "width": obj.width * self.scaling,
                    "height": obj.height * self.scaling
                }

        # player spawn
        for obj in tmx_map.get_layer_by_name("player"):
            if obj.name == player_start_pos:
                self.player = Player(pos=(obj.x * self.scaling, obj.y * self.scaling),
                                     groups=self.all_sprites,
                                     game=self,
                                     save_stats=self.player_stats_saved)
                self.player.starting_pos = (obj.x * self.scaling, obj.y * self.scaling)

    def reset_game_init(self):
        self.rgb_color = random.randint(0, 90), random.randint(0, 90), random.randint(0, 90)
        self.keys = {}
        self.mouse_button = {}
        self.mouse_pos = []
        self.pause = False
        self.reset_game_setup()
        self.reset_all_timer()
        self.clearing_sprites_group()
        self.clearing_enemy_and_item()
        self.load_setup = False
        self.reset_player_pos()
        self.actual_time = None
        self.previous_time = None
        self.pause_start_time = 0
        self.paused_time = 0
        self.round_menu = False
        self.time_before_next_round = None
        self.start_time = pygame.time.get_ticks()

    def reset_game_setup(self):
        self.player_stats_saved = {}
        self.previous_round = 1
        self.actual_round = 1
        self.time_per_round = 20  # sec
        self.wave_mob_time = 10  # sec
        self.actual_spawn_time = None
        self.last_spawn_time = -1
        self.nb_of_mob = None

    def reset_all_timer(self):
        self.start_time = pygame.time.get_ticks()
        self.actual_time = 0
        self.previous_time = None
        self.pause_start_time = 0
        self.paused_time = 0

        self.spawn_pause_start_time = 0
        self.spawn_paused_time = 0
        self.actual_spawn_time = 0
        self.last_spawn_time = -1

    def reset_player_pos(self):
        self.player.rect.topleft = self.player.starting_pos

    def clearing_sprites_group(self):
        self.all_sprites.empty()
        self.collision_sprites.empty()

    def clearing_enemy_and_item(self):
        for enemy in self.enemy_spawner.enemy_group:
            enemy.kill()
        for potion in self.all_sprites:
            if isinstance(potion, Item):
                potion.kill()

    def next_round(self):
        self.clearing_enemy_and_item()
        self.reset_player_pos()
        self.actual_round += 1
        if self.actual_round > self.previous_round + 1:
            self.previous_round += 1
        self.time_per_round = int(round(self.base_time_per_round + (self.base_time_per_round *
                                                                    (self.actual_round * 0.15)), -1))
        self.reset_all_timer()
        self.time_before_next_round = None
        self.round_menu = False

    def delete_save(self):
        with open(self.save_file, "r") as f:
            data = json.load(f)
            for keys in data:
                if keys == "save_activate":
                    data["save_activate"] = False
                else:
                    data[keys] = ""

        with open(self.save_file, 'w') as f:
            json.dump(data, f, indent=4)
            self.temporary_save = {}
            self.temporary_save = data
