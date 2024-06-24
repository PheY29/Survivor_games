import pygame
import sys
import os

from game_management import GameStateManager, ColorManager
from game import Game
from menu import Start, Pause, Setting, RoundMenu, DeathMenu

os.environ['SDL_VIDEO_CENTERED'] = '1'
pygame.init()

clock = pygame.time.Clock()
FPS = 60
RESOLUTION = {"720p": [1280, 720],
              "1080p": [1920, 1080]
              }
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

pygame.display.set_caption("Survivor")
screen = pygame.display.set_mode(RESOLUTION.get("720p"), pygame.RESIZABLE)

game_state_manager = GameStateManager("start")
color_manager = ColorManager(screen)
game = Game(screen, game_state_manager, color_manager)
start = Start(screen, game, game_state_manager, color_manager)
pause = Pause(screen, game, start, game_state_manager, color_manager)
setting = Setting(screen, game, start, pause, game_state_manager, color_manager)
round_menu = RoundMenu(screen, game, game_state_manager, color_manager)
death_menu = DeathMenu(screen, game, game_state_manager, color_manager)


states = {
    "game": game,
    "start": start,
    "pause": pause,
    "setting": setting,
    "round_menu": round_menu,
    "death_menu": death_menu
}

running = True

while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if game_state_manager.get_state() == "start":
            start.mouse_button = pygame.mouse.get_pressed()
            start.mouse_pos = pygame.mouse.get_pos()
            if event.type == pygame.KEYDOWN:
                start.keys[event.key] = True
            if event.type == pygame.KEYUP:
                start.keys[event.key] = False
        else:
            if not game.pause:
                if game_state_manager.get_state() == "game":
                    game.mouse_button = pygame.mouse.get_pressed()
                    game.mouse_pos = pygame.mouse.get_pos()
                    if event.type == pygame.KEYDOWN:
                        game.keys[event.key] = True
                    if event.type == pygame.KEYUP:
                        game.keys[event.key] = False

                elif game_state_manager.get_state() == "setting":
                    setting.mouse_button = pygame.mouse.get_pressed()
                    setting.mouse_pos = pygame.mouse.get_pos()
                    if event.type == pygame.KEYDOWN:
                        setting.keys[event.key] = True
                        setting.event = event
                    if event.type == pygame.KEYUP:
                        setting.keys[event.key] = False

            else:
                if game_state_manager.get_state() == "pause":
                    pause.mouse_button = pygame.mouse.get_pressed()
                    pause.mouse_pos = pygame.mouse.get_pos()
                    if event.type == pygame.KEYDOWN:
                        pause.keys[event.key] = True
                    if event.type == pygame.KEYUP:
                        pause.keys[event.key] = False

    states[game_state_manager.get_state()].run()

    pygame.display.update()
    clock.tick(FPS)

pygame.quit()
sys.exit()
