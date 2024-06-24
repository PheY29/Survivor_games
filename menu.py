import pygame
import json
import sys
import random


class Start:
    def __init__(self, screen, game, game_state_manager, color_manager):
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()
        self.game = game
        self.game_state_manager = game_state_manager
        self.color_manager = color_manager
        self.font = pygame.font.Font("assets/font.ttf", size=40)
        self.save_file = "others/save.json"
        self.import_save()
        self.save_state = False
        self.save_checked = False

        self.text_rects = {}
        self.keys = {}
        self.mouse_button = {}
        self.mouse_pos = []

        self.default_color = [[255, 153, 102], [255, 153, 102], [255, 153, 102]]
        self.base_color_direction = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        self.color_direction = [[-1, -1, 1], [-1, -1, 1], [-1, -1, 1]]

        self.play_selected = False
        self.continue_selected = False
        self.setting_selected = False
        self.quit_selected = False
        self.mouse_left_click = False

        self.text_infos = [
            ["Play", self.width // 2, self.height // 2],
            ["Setting", self.width // 2, self.height // 2 + 50],
            ["Quit", self.width // 2, self.height // 2 + 100]
        ]

    def run(self):
        self.check_save()
        self.update_screen()
        self.handle_input()

    def update_screen(self):
        self.screen.fill("aquamarine4")

        for i, (text, x, y) in enumerate(self.text_infos):
            self.text_rects[text] = self.color_manager.get_text_rect(text, 40, x, y)
            self.color_manager.color_text(self.default_color[i], self.base_color_direction[i], 5, text, 40, x, y)

    def handle_input(self):
        try:
            if self.keys.get(pygame.K_ESCAPE) or (self.text_rects["Quit"].collidepoint(self.mouse_pos)
                                                  and self.mouse_button[0] and not self.mouse_left_click):
                if (self.game.temporary_save["save_activate"]
                        and self.game_state_manager.get_previous_state() in ["round_menu", "setting"]):
                    with open(self.save_file, 'w') as f:
                        json.dump(self.game.temporary_save, f, indent=4)

                pygame.quit()
                sys.exit()

            ############
            for button_name, button_rect in self.text_rects.items():
                setattr(self, button_name.lower() + '_selected', button_rect.collidepoint(self.mouse_pos))

                selected_values = [self.play_selected, self.setting_selected, self.quit_selected]
                if self.save_state:
                    selected_values.append(self.continue_selected)

                for i, selected in enumerate(selected_values):
                    if selected:
                        self.base_color_direction[i] = self.color_direction[i]
                        for j in range(3):
                            self.default_color[i][j] = max(min(self.default_color[i][j], 255), 0)
                    else:
                        self.default_color[i] = [255, 153, 102]
                        self.base_color_direction[i] = [0, 0, 0]
            ############

            if (self.text_rects["Play"].collidepoint(self.mouse_pos) and self.mouse_button[0]
                    and not self.mouse_left_click):
                self.mouse_left_click = True
                self.game_state_manager.set_state("game")

            if self.save_state:
                if (self.text_rects["Continue"].collidepoint(self.mouse_pos) and self.mouse_button[0]
                        and not self.mouse_left_click):
                    self.mouse_left_click = True
                    self.inject_save()
                    self.game_state_manager.set_state("game")
                    pass

            if (self.text_rects["Setting"].collidepoint(self.mouse_pos) and self.mouse_button[0]
                    and not self.mouse_left_click):
                self.mouse_left_click = True
                self.game_state_manager.set_state("setting")

            if not self.mouse_button[0]:
                self.mouse_left_click = False

        except TypeError:
            pass

    def import_save(self):
        with open(self.save_file, "r") as f:
            data = json.load(f)
            for key, value in data.items():
                if key == "save_activate":
                    self.game.temporary_save[key] = True if value else False
                else:
                    self.game.temporary_save[key] = value

    def check_save(self):
        try:
            if not self.save_checked:
                if self.game.temporary_save["save_activate"]:
                    self.default_color.append([255, 153, 102])
                    self.base_color_direction.append([0, 0, 0])
                    self.color_direction.append([-1, -1, 1])
                    self.text_infos[0][2] -= 50
                    self.text_infos.append(["Continue", self.width // 2, self.height // 2])
                    self.save_state = True
                else:
                    if self.game_state_manager.get_previous_state() in ["round_menu", "death_menu"]:
                        self.text_infos = [item for item in self.text_infos if item[0] != "Continue"]
                        self.text_infos[0][2] += 50
                        self.default_color.remove([255, 153, 102])
                        self.base_color_direction.remove([0, 0, 0])
                        self.color_direction.remove([-1, -1, 1])
                    self.save_state = False

                self.save_checked = True

            if self.game_state_manager.get_previous_state() == "round_menu":
                if not self.save_state and self.game.temporary_save["save_activate"]:
                    self.save_checked = not self.save_checked

            elif self.game_state_manager.get_previous_state() == "death_menu":
                if self.save_state and not self.game.temporary_save["save_activate"]:
                    self.save_checked = not self.save_checked

        except KeyError:
            pass

    def inject_save(self):
        game_keys = {
            "actual_round": lambda value: setattr(self.game, "actual_round", value),
        }

        player_stats_keys = [
            "level", "experience", "total_experience", "health", "attack", "defense", "bullet_cd", "bullet_spd"
        ]

        enemy_keys = {
            "total_spawned_monster": lambda value: setattr(self.game.enemy_spawner, "total_spawned_monster",
                                                           value),
            "total_killed_monster": lambda value: setattr(self.game.enemy_spawner, "total_killed_monster",
                                                          value),
            "min_nb_of_monsters": lambda value: setattr(self.game, "min_nb_of_monsters", value),
            "max_nb_of_monsters": lambda value: setattr(self.game, "max_nb_of_monsters", value),
        }

        with open(self.save_file, "r") as f:
            data = json.load(f)
            if not data["save_activate"] and self.game_state_manager.get_previous_state() in ["round_menu", "setting"]:
                for key, value in self.game.temporary_save.items():
                    if key in game_keys:
                        game_keys[key](value)
                    elif key in player_stats_keys:
                        self.game.player_stats_saved[key] = value
                    elif key in enemy_keys:
                        enemy_keys[key](value)
            else:
                for key, value in data.items():
                    if key in game_keys:
                        game_keys[key](value)
                    elif key in player_stats_keys:
                        self.game.player_stats_saved[key] = value
                    elif key in enemy_keys:
                        enemy_keys[key](value)

    def reset_start_menu(self):
        self.keys = {}
        self.mouse_pos = []
        self.default_color = [[255, 153, 102], [255, 153, 102], [255, 153, 102]]
        self.base_color_direction = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        self.color_direction = [[-1, -1, 1], [-1, -1, 1], [-1, -1, 1]]

        self.save_checked = False
        self.save_state = False
        self.text_infos = [
            ["Play", self.width // 2, self.height // 2],
            ["Setting", self.width // 2, self.height // 2 + 50],
            ["Quit", self.width // 2, self.height // 2 + 100]
        ]

        self.play_selected = False
        self.continue_selected = False
        self.setting_selected = False
        self.quit_selected = False


class Setting:
    def __init__(self, screen, game, start, pause, game_state_manager, color_manager):
        self.screen = screen
        self.width = self.screen.get_width()
        self.height = self.screen.get_height()
        self.game = game
        self.start = start
        self.pause = pause
        self.game_state_manager = game_state_manager
        self.color_manager = color_manager

        self.font = pygame.font.Font("assets/font.ttf", size=40)
        self.json_file = "others/setting.json"

        with open(self.json_file, "r") as f:
            self.configurations = json.load(f)

        self.text_rects = {}
        self.button_rects = {}
        self.keys = {}
        self.mouse_button = {}
        self.mouse_pos = []

        self.default_color = [[255, 153, 102], [255, 153, 102]]
        self.base_color_direction = [[0, 0, 0], [0, 0, 0]]
        self.color_direction = [[-1, -1, 1], [-1, -1, 1]]

        self.return_selected = False
        self.save_selected = False
        self.mouse_left_click = True

        self.event = None
        self.loading_setting = []
        self.user_text = ""
        self.drawing_text = False

    def run(self):
        self.update_screen()
        self.handle_input()

    def update_screen(self):
        self.screen.fill("gray38")

        text_infos = [
            ("Setting", self.width // 2, self.height // 3 - 100, 50),
            ("Resolution", self.width // 2 - 125, self.height // 3, 30),
            ("Up", self.width // 2 - 125, self.height // 3 + 50, 30),
            ("Down", self.width // 2 - 125, self.height // 3 + 100, 30),
            ("Left", self.width // 2 - 125, self.height // 3 + 150, 30),
            ("Right", self.width // 2 - 125, self.height // 3 + 200, 30),
            ("Escape", self.width // 2 - 125, self.height // 3 + 250, 30)
        ]

        return_button_rect = pygame.Rect(self.width // 2 - 200, self.height // 3 + 350, 150, 50)
        save_button_rect = pygame.Rect(self.width // 2 + 50, self.height // 3 + 350, 150, 50)
        text_infos2 = [
            ("Return", return_button_rect.center[0], return_button_rect.center[1], 30),
            ("Save", save_button_rect.center[0], save_button_rect.center[1], 30)
        ]

        for i, (text, x, y, size) in enumerate(text_infos):
            self.text_rects[text] = self.color_manager.get_text_rect(text, size, x, y)
            if text != "Setting":
                if text == "Resolution":
                    for j in range(2):
                        button_rect = pygame.Rect(x + 190 + (j * 180), y - 13.5, 150, 35)
                        pygame.draw.rect(self.screen, (150, 150, 150), button_rect)
                        self.button_rects[text + "_button" + f"{j}"] = button_rect
                else:
                    button_rect = pygame.Rect(x + 190, y - 13.5, 120, 35)
                    pygame.draw.rect(self.screen, (150, 150, 150), button_rect)
                    self.button_rects[text + "_button"] = button_rect

            self.color_manager.color_text([255, 153, 102], [0, 0, 0], 5, text, size, x, y)

        for i, (text, x, y, size) in enumerate(text_infos2):
            self.text_rects[text] = self.color_manager.get_text_rect(text, size, x, y)

            if text == "Return":
                pygame.draw.rect(self.screen, (150, 150, 150), return_button_rect)
            elif text == "Save":
                pygame.draw.rect(self.screen, (150, 150, 150), save_button_rect)

            self.color_manager.color_text(self.default_color[i], self.base_color_direction[i], 5, text, size, x, y)

        self.loading_setting = [
            ("720p", str(self.configurations["720p"])[1:-1].replace(", ", "x"),
             self.button_rects["Resolution_button0"]),
            ("1080p", str(self.configurations["1080p"])[1:-1].replace(", ", "x"),
             self.button_rects["Resolution_button1"]),
            ("Up", self.configurations["up"], self.button_rects["Up_button"]),
            ("Down", self.configurations["down"], self.button_rects["Down_button"]),
            ("Left", self.configurations["left"], self.button_rects["Left_button"]),
            ("Right", self.configurations["right"], self.button_rects["Right_button"]),
            ("Escape", self.configurations["escape"], self.button_rects["Escape_button"])
        ]

        for i, (button_name, value, rect) in enumerate(self.loading_setting):
            self.color_manager.draw_text(value, 20, [255, 153, 102], rect.center[0], rect.center[1])

    def handle_input(self):
        try:
            for button_name, button_rect in self.text_rects.items():
                if button_name in ["Return", "Save"]:
                    setattr(self, button_name.lower() + '_selected', button_rect.collidepoint(self.mouse_pos))

                    selected_values = [self.return_selected, self.save_selected]
                    for i, selected in enumerate(selected_values):
                        if selected:
                            self.base_color_direction[i] = self.color_direction[i]
                            for j in range(3):
                                self.default_color[i][j] = max(min(self.default_color[i][j], 255), 0)
                        else:
                            self.default_color[i] = [255, 153, 102]
                            self.base_color_direction[i] = [0, 0, 0]

            if (self.text_rects["Return"].collidepoint(self.mouse_pos) and self.mouse_button[0]
                    and not self.mouse_left_click):
                self.mouse_left_click = True
                self.start.reset_start_menu()
                self.game_state_manager.set_state("start")
                self.game.screen = self.screen
                self.reset_setting_menu()

            if (self.text_rects["Save"].collidepoint(self.mouse_pos) and self.mouse_button[0]
                    and not self.mouse_left_click):
                self.mouse_left_click = True
                self.save_configurations()

            for name, rect in self.button_rects.items():
                if rect.collidepoint(self.mouse_pos):
                    pygame.draw.rect(self.screen, (200, 200, 200), rect, 5)

                    if "Resolution" in name:
                        if self.mouse_button[0] and not self.mouse_left_click:
                            resolution = ""
                            if "0" in name:
                                resolution = "720p"
                            elif "1" in name:
                                resolution = "1080p"

                            if resolution:
                                x, y = self.configurations[resolution]
                                self.screen = pygame.display.set_mode((x, y), pygame.RESIZABLE)
                                self.change_resolution(x, y)
                                self.game.clearing_sprites_group()
                                self.game.reset_game_setup()
                                self.pause.reset_pause_menu()
                                self.game.load_setup = False

                    elif self.mouse_button[0] and not self.mouse_left_click:
                        self.drawing_text = True

                        while self.drawing_text:
                            input_rect = pygame.Rect(rect)
                            pygame.draw.rect(self.screen, (150, 150, 150), input_rect)
                            pygame.draw.rect(self.screen, (200, 200, 200), rect, 5)
                            self.color_manager.draw_text("Press New Key", 20, [255, 153, 0],
                                                         input_rect.center[0] + 200, input_rect.center[1], 255)

                            self.handle_event_input()

                            key_already_assigned = False
                            for action, assigned_key in self.configurations.items():  # up, z / down, s...
                                if action != name.split("_")[0].lower() and assigned_key == self.user_text:
                                    # True : down != up (wanted) and s == s (wanted)
                                    # False : up not != up (wanted) and z (old) == z or anything (wanted)
                                    key_already_assigned = True
                                    break

                            if not key_already_assigned:
                                self.color_manager.draw_text(self.user_text, 20, [255, 153, 102], input_rect.center[0],
                                                             input_rect.center[1])

                                if self.user_text:
                                    self.modify_configurations(name.split("_")[0].lower(), self.user_text)
                                    self.user_text = ""
                                    self.drawing_text = False
                            else:
                                self.color_manager.draw_text("Key Already Assigned", 20, [255, 153, 0], self.width // 2,
                                                             self.height // 3 + 325, 255)
                                self.user_text = ""

                            pygame.display.update()

            if not self.mouse_button[0]:
                self.mouse_left_click = False

        except TypeError:
            pass

    def handle_event_input(self):
        for event in pygame.event.get():
            self.mouse_button = pygame.mouse.get_pressed()
            self.mouse_pos = pygame.mouse.get_pos()
            if event.type == pygame.KEYDOWN:
                self.keys[event.key] = True
                self.event = event
            if event.type == pygame.KEYUP:
                self.keys[event.key] = False

        if self.event:
            if self.drawing_text:
                if self.keys.get(pygame.K_BACKSPACE):
                    self.user_text = self.user_text[:-1]
                else:
                    if self.event.key == 27:
                        self.user_text = "ESCAPE"
                    elif self.event.unicode.isalpha() and len(self.user_text) < 1:
                        self.user_text += self.event.unicode

                self.event = None

    def modify_configurations(self, key, value):
        self.configurations[key] = value

    def save_configurations(self):
        end_time = pygame.time.get_ticks() + 500
        show_message = True

        with open(self.json_file, 'w') as f:
            json.dump(self.configurations, f, indent=4)
        self.game.import_config()

        while show_message:
            current_time = pygame.time.get_ticks()
            if current_time > end_time:
                show_message = False
            if show_message:
                self.color_manager.draw_text("Setting Saved", 20, [255, 153, 0], self.width // 2,
                                             self.height // 3 + 325, 255)

            pygame.display.update()

    def change_resolution(self, x, y):
        state_list = ["game", "start", "pause"]
        for state in state_list:
            state_obj = getattr(self, state)
            state_obj.screen = pygame.display.set_mode((x, y), pygame.RESIZABLE)
            state_obj.width = state_obj.screen.get_width()
            state_obj.height = state_obj.screen.get_height()

        self.width = self.screen.get_width()
        self.height = self.screen.get_height()

    def reset_setting_menu(self):
        self.keys = {}
        self.mouse_pos = []
        self.default_color = [[255, 153, 102], [255, 153, 102]]
        self.base_color_direction = [[0, 0, 0], [0, 0, 0]]
        self.color_direction = [[-1, -1, 1], [-1, -1, 1]]
        self.return_selected = False
        self.save_selected = False


class Pause:
    def __init__(self, screen, game, start, game_state_manager, color_manager):
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()
        self.game = game
        self.start = start
        self.game_state_manager = game_state_manager
        self.color_manager = color_manager

        self.font = pygame.font.Font("assets/font.ttf", size=40)
        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        self.text_rects = {}
        self.keys = {}
        self.mouse_button = {}
        self.mouse_pos = []

        self.default_color = [[255, 153, 102], [255, 153, 102], [255, 153, 102]]
        self.base_color_direction = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        self.color_direction = [[-1, -1, 1], [-1, -1, 1], [-1, -1, 1]]
        self.text_opacity = 0
        self.max_text_opacity = 255
        self.text_appear_speed = 1

        self.resume_selected = False
        self.restart_selected = False
        self.quit_selected = False
        self.mouse_left_click = True

    def run(self):
        self.update_screen()
        self.handle_input()

    def update_screen(self):
        pygame.draw.rect(self.surface, (128, 128, 128, 1), [0, 0, self.width, self.height])
        self.screen.blit(self.surface, (0, 0))

        self.color_manager.color_text([255, 153, 102], [0, 0, 0], 5, "Paused", 50, self.width // 2,
                                      self.height // 2 - 100, self.text_opacity)

        text_infos = [
            ("Resume", self.width // 2, self.height // 2 + 100, 30),
            ("Restart", self.width // 2, self.height // 2 + 150, 30),
            ("Quit", self.width // 2, self.height // 2 + 200, 30)
        ]

        for i, (text, x, y, size) in enumerate(text_infos):
            self.text_rects[text] = self.color_manager.get_text_rect(text, size, x, y)
            self.color_manager.color_text(self.default_color[i], self.base_color_direction[i], 5, text, size, x, y,
                                          self.text_opacity)

        self.check_opacity()

    def check_opacity(self):
        if self.text_opacity < self.max_text_opacity:
            self.text_opacity += self.text_appear_speed

    def handle_input(self):
        try:
            for button_name, button_rect in self.text_rects.items():
                setattr(self, button_name.lower() + '_selected', button_rect.collidepoint(self.mouse_pos))

                selected_values = [self.resume_selected, self.restart_selected, self.quit_selected]
                for i, selected in enumerate(selected_values):
                    if selected:
                        self.base_color_direction[i] = self.color_direction[i]
                        for j in range(3):
                            self.default_color[i][j] = max(min(self.default_color[i][j], 255), 0)
                    else:
                        self.default_color[i] = [255, 153, 102]
                        self.base_color_direction[i] = [0, 0, 0]

            if (self.text_rects["Quit"].collidepoint(self.mouse_pos) and self.mouse_button[0]
                    and not self.mouse_left_click):
                self.mouse_left_click = True
                self.game.reset_game_init()
                self.start.reset_start_menu()
                self.game_state_manager.set_state("start")
                self.reset_pause_menu()

            if (self.text_rects["Resume"].collidepoint(self.mouse_pos)
                    and self.mouse_button[0] and not self.mouse_left_click):
                self.mouse_left_click = True
                self.game.pause = False
                self.game_state_manager.set_state("game")
                self.reset_pause_menu()

            if (self.text_rects["Restart"].collidepoint(self.mouse_pos) and self.mouse_button[0]
                    and not self.mouse_left_click):
                self.mouse_left_click = True
                self.game.reset_game_init()
                self.game_state_manager.set_state("game")
                self.text_opacity = 0

            if not self.mouse_button[0]:
                self.mouse_left_click = False

        except TypeError:
            pass

    def reset_pause_menu(self):
        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.keys = {}
        self.mouse_pos = []
        self.default_color = [[255, 153, 102], [255, 153, 102], [255, 153, 102]]
        self.base_color_direction = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        self.color_direction = [[-1, -1, 1], [-1, -1, 1], [-1, -1, 1]]
        self.text_opacity = 0
        self.resume_selected = False
        self.restart_selected = False
        self.quit_selected = False


class RoundMenu:
    def __init__(self, screen, game, game_state_manager, color_manager):
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()
        self.game = game
        self.game_state_manager = game_state_manager
        self.color_manager = color_manager
        self.start = Start(self.screen, self.game, self.game_state_manager, self.color_manager)

        self.font = pygame.font.Font("assets/font.ttf", size=30)
        self.bonus_font = pygame.font.Font("assets/font.ttf", size=20)
        self.save_file = "others/save.json"
        self.round_menu_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.rms_width = self.round_menu_surface.get_width()
        self.rms_height = self.round_menu_surface.get_height()

        self.default_color = [[255, 153, 102], [255, 153, 102]]
        self.base_color_direction = [[0, 0, 0], [0, 0, 0]]
        self.color_direction = [[-1, -1, 1], [-1, -1, 1]]
        self.continue_selected = False
        self.save_and_quit_selected = False

        self.mouse_left_click = False

        self.rects_for_bonus = {}
        self.texts_rects_for_menu = {}
        self.selected_bonus_rect = None
        self.bonus_attributes = {
            "health": {"type": "health",
                       "bonus": {"common": 2, "rare": 4, "epic": 8}},
            "attack": {"type": "attack",
                       "bonus": {"common": 1, "rare": 2, "epic": 4}},
            "defense": {"type": "defense",
                        "bonus": {"common": 0.5, "rare": 1, "epic": 2}},
            "bullet_cd": {"type": "bullet_cooldown",
                          "limit": 5,
                          "bonus": {"common": 0.5, "rare": 1, "epic": 1.5}},
            "bullet_spd": {"type": "bullet_speed",
                           "limit": 17,
                           "bonus": {"common": 0.2, "rare": 0.5, "epic": 1}}
        }
        self.bonus_randomized = False
        self.bonus_choices = ["left", "middle", "right"]
        self.bonus_color = {
            "common": "seagreen4",
            "rare": "royalblue4",
            "epic": "purple4"
        }
        self.selected_bonuses = {
            "left": None,
            "middle": None,
            "right": None
        }
        self.bonus_chosen = None

        self.rect_round = {
            # self.round_menu_surface : start at x 320 + width 640 so surface of 960
            # 4 space + 3 rect with 640 surface = (4 * 52) + (196 * 3)
            # middle: surface//2 - his surface//2 so 640 - (2*self.round_menu_surface.get_width()//6.5)= 640-98 = x= 542
            # left : x = 320 + 13 = 333 + 196 so 1280 (total screen width) / 333 = 3.84% of total width
            # right : x = middle width + half middle + space = 640 + 96 + 13 = 749 so 1280/ 749 = 1.7% of total width
            "menu": ("gray48", self.rms_width // 4, self.rms_height // 4, self.rms_width // 2, self.rms_height // 2),
            "left": (
                "peachpuff2", self.rms_width // 3.84, self.rms_height // 3, self.rms_width // 6.5,
                self.rms_height // 3),
            "middle": (
                "peachpuff2", self.rms_width // 2 - self.rms_width // 13, self.rms_height // 3,
                self.rms_width // 6.5, self.rms_height // 3),
            "right": (
                "peachpuff2", self.rms_width // 1.7, self.rms_height // 3, self.rms_width // 6.5, self.rms_height // 3),
        }
        self.text_round = [
            ("Round Clear", self.rms_width // 2, self.rms_height // 3.75),
            ("Continue", self.rms_width // 1.50, self.rms_height // 4 + self.rms_height // 2.35),
            ("Save and Quit", self.rms_width // 2.7, self.rms_height // 4 + self.rms_height // 2.35)
        ]

    def run(self):
        self.randomize_bonuses()
        self.update_screen()
        self.handle_input()

    def randomize_bonuses(self):
        if not self.bonus_randomized:
            for choice in self.bonus_choices:
                while True:
                    stats = random.choice(list(self.bonus_attributes.keys()))
                    rarity = random.choices(["common", "rare", "epic"], weights=[70, 20, 10])[0]
                    bonus = self.bonus_attributes[stats]["bonus"][rarity]

                    if stats == "bullet_cd":
                        player_stat = getattr(self.game.player, stats)
                        if player_stat - bonus >= self.bonus_attributes[stats]["limit"]:  # 15 - bonus >= 5
                            self.selected_bonuses[choice] = {
                                "attribute": stats,
                                "rarity": rarity,
                                "bonus": bonus
                            }
                            break
                    elif stats == "bullet_spd":
                        player_stat = getattr(self.game.player, stats)
                        if player_stat + bonus <= self.bonus_attributes[stats]["limit"]:  # 10 + bonus <= 20
                            self.selected_bonuses[choice] = {
                                "attribute": stats,
                                "rarity": rarity,
                                "bonus": bonus
                            }
                            break
                    else:
                        self.selected_bonuses[choice] = {
                            "attribute": stats,
                            "rarity": rarity,
                            "bonus": bonus
                        }
                        break
            self.bonus_randomized = True

    def update_screen(self):
        for name, info in self.rect_round.items():
            color, x, y, width, height = info[0], info[1], info[2], info[3], info[4]
            self.rects_for_bonus[name] = pygame.Rect(x, y, width, height)
            pygame.draw.rect(self.round_menu_surface, color, (x, y, width, height))

            if name in self.selected_bonuses:
                bonus_info = self.selected_bonuses[name]
                sign = "-" if bonus_info['attribute'] == "bullet_cd" else "+"
                attribute_text = f"{bonus_info['attribute'].capitalize()}".replace("_", " ")
                bonus_text = f"{sign}{bonus_info['bonus']}"
                rarity_text = f"({bonus_info['rarity'].capitalize()})"
                all_texts = [attribute_text, bonus_text, rarity_text]

                rarity_color = self.bonus_color[bonus_info["rarity"]]

                for i, text in enumerate(all_texts):
                    if i == 2:
                        text_surface = self.bonus_font.render(text, True, rarity_color)
                    else:
                        text_surface = self.bonus_font.render(text, True, (0, 0, 0))
                    self.round_menu_surface.blit(text_surface, (x + (width - text_surface.get_width()) // 2,
                                                                y + (height - text_surface.get_height()) // 3 + (
                                                                        i * 25)))

        for i, (text, x, y) in enumerate(self.text_round):
            text_rect = self.font.render(text, True, (255, 153, 102))
            x -= text_rect.get_width() // 2

            if text != "Round Clear":
                i -= 1
                self.color_manager.color_text(self.default_color[i], self.base_color_direction[i], 5, text, 30, x, y,
                                              surf=self.round_menu_surface, centered=False)
            else:
                self.color_manager.color_text([255, 153, 102], [0, 0, 0], 5, text, 30, x, y,
                                              surf=self.round_menu_surface,
                                              centered=False)
            self.texts_rects_for_menu[text] = self.color_manager.get_text_rect(text, 30, x, y, centered=False)

        self.screen.blit(self.round_menu_surface, (0, 0))

    def handle_input(self):
        mouse_button = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()

        for button_name, button_rect in self.texts_rects_for_menu.items():
            if button_name == "Save and Quit":
                button_name = button_name.replace(" ", "_")

            setattr(self, button_name.lower() + '_selected', button_rect.collidepoint(mouse_pos))
            selected_values = [self.continue_selected, self.save_and_quit_selected]
            for i, selected in enumerate(selected_values):
                if selected:
                    self.base_color_direction[i] = self.color_direction[i]
                    for j in range(3):
                        self.default_color[i][j] = max(min(self.default_color[i][j], 255), 0)
                else:
                    self.default_color[i] = [255, 153, 102]
                    self.base_color_direction[i] = [0, 0, 0]

        for name, rect in self.rects_for_bonus.items():
            if rect.collidepoint(mouse_pos) and name != "menu":
                if mouse_button[0] and not self.mouse_left_click:
                    self.selected_bonus_rect = rect
                    self.bonus_chosen = self.selected_bonuses[name]
                    self.mouse_left_click = True
                pygame.draw.rect(self.screen, (150, 150, 150), rect, 5)

        if self.selected_bonus_rect:
            pygame.draw.rect(self.screen, (50, 50, 50), self.selected_bonus_rect, 5)

        if (self.texts_rects_for_menu["Save and Quit"].collidepoint(mouse_pos) and mouse_button[0]
                and not self.mouse_left_click):
            self.mouse_left_click = True
            self.temporary_save()
            self.game.reset_game_init()
            self.start.reset_start_menu()
            self.game_state_manager.set_state("start")

        if (self.texts_rects_for_menu["Continue"].collidepoint(mouse_pos) and mouse_button[0]
                and not self.mouse_left_click and self.selected_bonus_rect):
            self.mouse_left_click = True
            self.apply_bonus(self.bonus_chosen)
            self.game_state_manager.set_state("game")
            self.reset_round_menu()

        if not mouse_button[0]:
            self.mouse_left_click = False

    def apply_bonus(self, selected_bonus):
        attribute = selected_bonus["attribute"]
        bonus = selected_bonus["bonus"]

        if attribute == "health":
            self.game.player.health += bonus
            self.game.player.base_health += bonus
        elif attribute == "attack":
            self.game.player.attack += bonus
        elif attribute == "defense":
            self.game.player.defense += bonus
        elif attribute == "bullet_cd":
            self.game.player.bullet_cd -= bonus
        elif attribute == "bullet_spd":
            self.game.player.bullet_spd += bonus

    def reset_round_menu(self):
        self.default_color = [[255, 153, 102], [255, 153, 102]]
        self.base_color_direction = [[0, 0, 0], [0, 0, 0]]
        self.color_direction = [[-1, -1, 1], [-1, -1, 1]]
        self.continue_selected = False
        self.quit_selected = False
        self.mouse_left_click = False
        self.selected_bonus_rect = None
        self.bonus_randomized = False
        self.bonus_chosen = None

    def temporary_save(self):
        self.game.temporary_save = {
            "save_activate": True,
            "actual_round": self.game.actual_round,
            "level": self.game.player.level,
            "experience": self.game.player.experience,
            "total_experience": self.game.player.total_experience,
            "health": self.game.player.health,
            "attack": self.game.player.attack,
            "defense": self.game.player.defense,
            "bullet_cd": self.game.player.bullet_cd,
            "bullet_spd": self.game.player.bullet_spd,
            "total_spawned_monster": self.game.enemy_spawner.total_spawned_monster,
            "total_killed_monster": self.game.enemy_spawner.total_killed_monster,
            "min_nb_of_monsters": self.game.min_nb_of_monsters,
            "max_nb_of_monsters": self.game.max_nb_of_monsters
        }


class DeathMenu:
    def __init__(self, screen, game, game_state_manager, color_manager):
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()
        self.game = game
        self.game_state_manager = game_state_manager
        self.color_manager = color_manager
        self.start = Start(self.screen, self.game, self.game_state_manager, self.color_manager)

        self.death_menu_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.dms_width = self.death_menu_surface.get_width()
        self.dms_height = self.death_menu_surface.get_height()
        self.font = pygame.font.Font("assets/font.ttf", size=30)

        self.default_color = [[255, 153, 102]]
        self.base_color_direction = [[0, 0, 0]]
        self.color_direction = [[-1, -1, 1]]
        self.return_selected = False
        self.mouse_left_click = False

        self.all_rects = {
            "principal_menu": ("gray48", self.dms_width // 6, self.dms_height // 6,
                               self.dms_width // 1.5, self.dms_height // 1.5, 0),
            "decoration_menu": ("gray30", self.dms_width // 6, self.dms_height // 6,
                                self.dms_width // 1.5, self.dms_height // 1.5, 5)
        }
        self.text_to_draw = [
            ("You'r die !", self.dms_width // 2, self.dms_height // 6 + 15),
            ("Return to main menu", self.dms_width // 2, self.dms_height // 1.31),
            ("Your final statistic: ", self.dms_width // 2, self.dms_height // 1.894)
        ]
        self.return_rect = {}
        self.infos_to_draw = [
            # to calcul % for y : total height = 720 / height wanted
            ("You have survived to ", self.dms_width // 2, self.dms_height // 4),
            ("Your final level is: ", self.dms_width // 2, self.dms_height // 3.348),
            ("Total experience: ", self.dms_width // 2, self.dms_height // 2.88),
            ("Appeared monster: ", self.dms_width // 2, self.dms_height // 2.52),
            ("Killed monster: ", self.dms_width // 2, self.dms_height // 2.25),

            ("Health: ", self.dms_width // 3, self.dms_height // 1.69),
            ("Attack: ", self.dms_width // 3, self.dms_height // 1.56),
            ("Defense: ", self.dms_width // 3, self.dms_height // 1.45),
            ("Bullet cd: ", self.dms_width // 1.5, self.dms_height // 1.69),
            ("bullet spd: ", self.dms_width // 1.5, self.dms_height // 1.56),
        ]

    def run(self):
        self.update_screen()
        self.handle_input()

    def update_screen(self):
        stats_variable = [self.game.actual_round, self.game.player.level, self.game.player.total_experience,
                          self.game.enemy_spawner.total_spawned_monster, self.game.enemy_spawner.total_killed_monster,
                          self.game.player.health, self.game.player.attack, self.game.player.defense,
                          self.game.player.bullet_cd, self.game.player.bullet_spd
                          ]

        for name, info in self.all_rects.items():
            color, x, y, width, height, thickness = info[0], info[1], info[2], info[3], info[4], info[5]
            pygame.draw.rect(self.death_menu_surface, color, (x, y, width, height), thickness)

        for i, (text, x, y) in enumerate(self.text_to_draw):
            text_rect = self.font.render(text, True, (255, 153, 102))
            x -= text_rect.get_width() // 2

            if text == "Return to main menu":
                i = 0
                self.color_manager.color_text(self.default_color[i], self.base_color_direction[i], 5, text, 30, x, y,
                                              surf=self.death_menu_surface, centered=False)
                self.return_rect[text] = self.color_manager.get_text_rect(text, 30, x, y, centered=False)
            else:
                self.death_menu_surface.blit(text_rect, (x, y))

        for i, (texts, x, y) in enumerate(self.infos_to_draw):
            stats_text = [str(stats) for stats in stats_variable]
            text = self.font.render(texts, True, (0, 0, 0))

            if i == 0:
                stats = stats_text[0] + " rounds"
                stats = self.font.render(stats, True, (220, 20, 60))
            else:
                stats = self.font.render(stats_text[i], True, (220, 20, 60))

            self.death_menu_surface.blit(text, (x - (text.get_width() + stats.get_width()) // 2, y))
            self.death_menu_surface.blit(stats, (x + (text.get_width() // 2 - stats.get_width() // 2) + 10, y))

        self.screen.blit(self.death_menu_surface, (0, 0))

    def handle_input(self):
        mouse_button = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()

        for button_name, button_rect in self.return_rect.items():
            button_name = button_name.replace("Return to main menu", "return")
            setattr(self, button_name.lower() + '_selected', button_rect.collidepoint(mouse_pos))

            selected_values = [self.return_selected]
            for i, selected in enumerate(selected_values):
                if selected:
                    self.base_color_direction[i] = self.color_direction[i]
                    for j in range(3):
                        self.default_color[i][j] = max(min(self.default_color[i][j], 255), 0)

                else:
                    self.default_color[i] = [255, 153, 102]
                    self.base_color_direction[i] = [0, 0, 0]

        if (self.return_rect["Return to main menu"].collidepoint(mouse_pos) and mouse_button[0]
                and not self.mouse_left_click):
            self.mouse_left_click = True
            self.start.reset_start_menu()
            self.game.reset_game_init()
            self.game_state_manager.set_state("start")
            self.reset_death_menu()

        if not mouse_button[0]:
            self.mouse_left_click = False

    def reset_death_menu(self):
        self.default_color = [[255, 153, 102]]
        self.base_color_direction = [[0, 0, 0]]
        self.color_direction = [[-1, -1, 1]]
        self.return_selected = False
        self.mouse_left_click = False
