import pygame


class GameStateManager:
    def __init__(self, current_state):
        self.current_state = current_state
        self.previous_state = None

    def get_state(self):
        return self.current_state

    def set_state(self, state):
        self.previous_state = self.current_state
        self.current_state = state

    def get_previous_state(self):
        return self.previous_state

    def remove_state_and_go_on(self, state):
        self.previous_state = None
        self.set_state(state)


class ColorManager:
    def __init__(self, screen):
        self.screen = screen
        self.black = (0, 0, 0)
        self.white = (255, 255, 255)
        self.minimum = 0
        self.maximum = 255

    def draw_text(self, text, size, color, x, y, opacity=255, surf=None, centered=True):
        font = pygame.font.Font("../Pong/assets/font.ttf", size)
        text_surface = font.render(text, True, color)
        text_surface.set_alpha(opacity)
        text_rect = text_surface.get_rect()
        if centered:
            text_rect.center = (x, y)
        else:
            text_rect.topleft = (x, y)

        if surf:
            surf.blit(text_surface, text_rect)
        else:
            self.screen.blit(text_surface, text_rect)

    def get_text_rect(self, text, size, x, y, color=(255, 255, 255), centered=True):
        font = pygame.font.Font("assets/font.ttf", size)
        text_surface = font.render(text, True, color)
        if centered:
            text_rect = text_surface.get_rect(center=(x, y))
        else:
            text_rect = text_surface.get_rect(topleft=(x, y))

        return text_rect

    def color_change(self, color, direction, speed):
        for i in range(3):
            color[i] += speed * direction[i]
            if color[i] >= self.maximum or color[i] <= self.minimum:
                direction[i] *= -1

    def color_text(self, color, direction, speed, text, size, x, y, opacity=255, surf=None, centered=True):
        self.draw_text(text, size, color, x, y, opacity, surf, centered)
        self.color_change(color, direction, speed)
