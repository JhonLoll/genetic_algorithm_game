import pygame

class Background:
    def __init__(self, width, height):
        # Carregar camadas
        self.layers = [
            pygame.image.load("game/assets/background/plx-1.png").convert(),
            pygame.image.load("game/assets/background/plx-2.png").convert_alpha(),
            pygame.image.load("game/assets/background/plx-3.png").convert_alpha(),
            pygame.image.load("game/assets/background/plx-4.png").convert_alpha(),
            pygame.image.load("game/assets/background/plx-5.png").convert_alpha(),
        ]
        self.layers = [pygame.transform.scale(item, (width, height)) for item in self.layers]

    def draw(self, screen):
        for layer in self.layers:
            screen.blit(layer, (0, 0))