import pygame

class Platform():
    def __init__(self, x, y):
        self.image = pygame.image.load("game/assets/ground.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (y * 2, 200))
        # self.rect = pygame.Rect(x, y, width, height)
        self.rect = self.image.get_rect(center=(0, x + 100))
    def draw(self, screen):
        screen.blit(self.image, self.rect)
        # pygame.draw.rect(screen, (23, 66, 38), self.rect)
        # Colisão da plataforma
        # pygame.draw.rect(screen, (255, 0, 0), self.rect, 2)