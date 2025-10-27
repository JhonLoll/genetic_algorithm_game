import pygame

class Apple:
    def __init__(self, x, y):
        self.image = pygame.image.load("game/assets/apple.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect(center=(x, y))

    def draw(self, screen):
        screen.blit(self.image, self.rect)