import pygame

class Platform():
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)

    def draw(self, screen):
        pygame.draw.rect(screen, (23, 66, 38), self.rect)
        # Colisão da plataforma
        pygame.draw.rect(screen, (255, 0, 0), self.rect, 2)