import pygame
import random
from components.background import Background
from components.apple import Apple
from components.platform import Platform
from genetic import GeneticAlgorithm

# Inicializa a instância do pygame
pygame.init()

# Predefinindo algumas cores
BLUE  = (0, 0, 255)
RED   = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY  = (100, 100, 100)

# Define o tamanho da tela
SCREEN_WIDTH, SCREEN_HEIGHT = 1020, 680

# Cria a tela
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Genetic Algorithm - Evolução de Criaturas")

# Configurações do jogo
GROUND_Y = SCREEN_HEIGHT - 100
GENERATION_TIME = 15  # segundos por geração
FPS = 60

# Components
bg = Background(SCREEN_WIDTH, SCREEN_HEIGHT)

# Spawn inicial aleatório da maçã (mantém margens para não sair da tela)
apple_x = random.randint(50, SCREEN_WIDTH - 50)
apple_y = 50
apple = Apple(apple_x, apple_y)

platform = Platform(GROUND_Y, SCREEN_WIDTH)

# Algoritmo Genético
ga = GeneticAlgorithm(population_size=100)
creatures = ga.create_population(SCREEN_WIDTH // 2, GROUND_Y)

# Controles
clock = pygame.time.Clock()
generation_timer = 0
paused = False

# Font para informações
font = pygame.font.Font(None, 32)
small_font = pygame.font.Font(None, 24)

# Loop principal
running = True
while running:
    delta_time = clock.tick(FPS) / 1000.0  # Delta time em segundos
    

    stats = ga.get_statistics(creatures)

    # Eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        elif event.type == pygame.VIDEORESIZE:
            SCREEN_WIDTH = event.w
            SCREEN_HEIGHT = event.h
            screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
            bg = Background(SCREEN_WIDTH, SCREEN_HEIGHT)
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Força todas as criaturas a pularem
                for c in creatures:
                    if c.alive:
                        c.jump()
            
            elif event.key == pygame.K_p:
                # Pausa/Resume
                paused = not paused
    
    if not paused:
        # Timer da geração
        generation_timer += delta_time

        # Atualiza criaturas
        all_dead = True
        best_creature = None
        for creature in creatures:
            if creature.alive:
                all_dead = False
                creature.update(
                    apple.rect.center, 
                    SCREEN_WIDTH, 
                    SCREEN_HEIGHT,
                    GROUND_Y,
                    delta_time,
                    creatures
                )

            # Identifica a melhor criatura
            if best_creature is None or creature.score > best_creature.score:
                best_creature = creature

        # Marca a melhor criatura
        for creature in creatures:
            creature.is_best = (creature == best_creature)

        # Evolui automaticamente quando todas morrerem ou tempo acabar
        if (all_dead or generation_timer >= GENERATION_TIME):
            
            print(f"Geração {ga.generation}: {stats}")
            
            creatures = ga.evolve(creatures, SCREEN_WIDTH // 2, GROUND_Y)
            # Respawna a maçã a cada nova geração para introduzir
            # variabilidade no ambiente (aleatoriedade no spawn)
            apple_x = random.randint(50, SCREEN_WIDTH - 50)
            apple_y = 50
            apple.rect.center = (apple_x, apple_y)
            generation_timer = 0
    
    # Desenha tudo
    bg.draw(screen)
    platform.draw(screen)
    apple.draw(screen)
    
    # Desenha criaturas
    for creature in creatures:
        creature.draw(screen)
    
    # Informações na tela
    # stats = ga.get_statistics(creatures)

    print(stats)
    
    # Geração
    gen_text = font.render(f"Geração: {ga.generation}", True, WHITE)
    screen.blit(gen_text, (10, 10))
    
    # Tempo restante
    time_left = max(0, GENERATION_TIME - generation_timer)
    timer_text = font.render(f"Tempo: {time_left:.1f}s", True, WHITE)
    screen.blit(timer_text, (10, 50))
    
    # Melhor fitness
    best_text = font.render(f"Melhor: {int(stats['best'])}", True, GREEN)
    screen.blit(best_text, (10, 90))
    
    # Fitness médio
    avg_text = small_font.render(f"Média: {int(stats['average'])}", True, WHITE)
    screen.blit(avg_text, (10, 130))
    
    # Criaturas vivas
    alive_count = sum(1 for c in creatures if c.alive)
    alive_text = small_font.render(f"Vivas: {alive_count}/{len(creatures)}", True, WHITE)
    screen.blit(alive_text, (10, 160))
    
    # Instruções
    instructions = [
        "ESPAÇO: Fazer criaturas pularem",
        "P: Pausar/Continuar",
    ]
    
    for i, instruction in enumerate(instructions):
        text = small_font.render(instruction, True, GRAY)
        screen.blit(text, (SCREEN_WIDTH - 300, 10 + i * 30))
    
    # Indicador de pausa
    if paused:
        pause_text = font.render("PAUSADO", True, RED)
        pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, 50))
        screen.blit(pause_text, pause_rect)
    
    # Histórico de fitness (gráfico simples)
    if len(ga.best_fitness_history) > 1:
        graph_x = SCREEN_WIDTH - 320
        graph_y = SCREEN_HEIGHT - 150
        graph_width = 300
        graph_height = 100
        
        # Fundo do gráfico
        pygame.draw.rect(screen, (30, 30, 30), (graph_x, graph_y, graph_width, graph_height))
        pygame.draw.rect(screen, WHITE, (graph_x, graph_y, graph_width, graph_height), 1)
        
        # Título
        graph_title = small_font.render("Evolução do Fitness", True, WHITE)
        screen.blit(graph_title, (graph_x + 70, graph_y - 25))
        
        # Desenha linha do gráfico
        max_fitness = max(ga.best_fitness_history) if ga.best_fitness_history else 1
        history_to_show = ga.best_fitness_history[-50:]  # Últimas 50 gerações
        
        if len(history_to_show) > 1:
            points = []
            for i, fitness in enumerate(history_to_show):
                x = graph_x + (i / (len(history_to_show) - 1)) * graph_width
                y = graph_y + graph_height - (fitness / max_fitness) * graph_height
                points.append((x, y))
            
            if len(points) > 1:
                pygame.draw.lines(screen, GREEN, False, points, 2)
    
    # Atualiza a tela
    pygame.display.flip()

pygame.quit()
