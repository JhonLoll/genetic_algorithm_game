import pygame
import random
import math

class Creature:
    def __init__(self, x, y, dna=None):
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(random.uniform(-0.5, 0.5), 0)
        self.alive = True
        self.score = 0
        self.on_ground = False
        self.can_jump = True
        self.standing_on = None  # Outra criatura
        
        # DNA: genes da criatura
        if dna is None:
            self.dna = {
                'leg_length': random.uniform(10, 30),
                'neck_length': random.uniform(7.5, 40),
                'body_size': random.uniform(7.5, 17.5),
                'jump_strength': random.uniform(2, 15),
                'color': (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255)),
                'jump_timing': random.uniform(1, 3.0)  # Quando pular em segundos
            }
        else:
            self.dna = dna
        
        self.jump_timer = 0
        self.has_jumped = False
        self.is_best = False  # Indica se a criatura é a melhor
        
    @property
    def mass(self):
        """Massa baseada no tamanho total"""
        return (self.dna['body_size'] + self.dna['leg_length'] + self.dna['neck_length']) / 15
    
    @property
    def total_height(self):
        """Altura total da criatura"""
        return self.dna['leg_length'] + self.dna['body_size'] + self.dna['neck_length']
    
    @property
    def head_pos(self):
        """Posição da cabeça"""
        return pygame.Vector2(self.pos.x, self.pos.y - self.total_height)
    
    def get_collision_rect(self):
        """Retângulo de colisão para empilhamento"""
        width = self.dna['body_size'] * 1.5
        height = self.total_height
        return pygame.Rect(
            self.pos.x - width/2,
            self.pos.y - height,
            width,
            height
        )

    def jump(self):
        """Pula considerando massa e força"""
        if self.can_jump and (self.on_ground or self.standing_on):
            # Força de pulo ajustada pela massa (criaturas mais pesadas pulam menos)
            jump_force = self.dna['jump_strength'] / math.sqrt(self.mass)
            self.vel.y = -jump_force
            self.on_ground = False
            self.standing_on = None
            self.can_jump = False
            self.has_jumped = True

    def update(self, target_pos, width, height, ground_y, delta_time, other_creatures):
        if not self.alive:
            return

        # Direção para a maçã (movimento direcionado)
        direction_to_target = pygame.Vector2(target_pos) - self.pos
        if direction_to_target.length() > 0:
            direction_to_target = direction_to_target.normalize()
        else:
            direction_to_target = pygame.Vector2(0, 0)

        # Ajusta a velocidade para seguir a direção da maçã
        self.vel.x = direction_to_target.x * 2  # Velocidade horizontal ajustada

        # Timer para pulo automático
        self.jump_timer += delta_time

        # Pula no tempo definido pelo DNA
        if not self.has_jumped and self.jump_timer >= self.dna['jump_timing']:
            self.jump()

        # Gravidade
        GRAVITY = 0.5
        if not self.on_ground and not self.standing_on:
            self.vel.y += GRAVITY
            self.vel.y = min(self.vel.y, 20)  # Velocidade máxima de queda

        # Atualiza posição
        self.pos += self.vel

        # Colisão com o chão
        if self.pos.y >= ground_y:
            self.pos.y = ground_y
            self.vel.y = 0
            self.on_ground = True
            self.can_jump = True
        else:
            self.on_ground = False

        # Verifica empilhamento com outras criaturas
        self.standing_on = None
        if self.vel.y > 0:  # Caindo
            for other in other_creatures:
                if other != self and other.alive:
                    other_rect = other.get_collision_rect()
                    my_rect = self.get_collision_rect()

                    # Se estou caindo sobre outra criatura
                    if (my_rect.colliderect(other_rect) and 
                        self.pos.y < other.pos.y and
                        abs(self.pos.x - other.pos.x) < self.dna['body_size']):

                        # Fica em cima da outra criatura
                        self.pos.y = other.pos.y - other.total_height - 5
                        self.vel.y = 0
                        self.standing_on = other
                        self.can_jump = True
                        break

        # Colisão com as paredes
        if self.pos.x < 0 or self.pos.x > width:
            self.alive = False

        # Cai abaixo do chão
        if self.pos.y > ground_y + 100:
            self.alive = False

        # Calcula pontuação (distância da cabeça até a maçã)
        head_pos = self.head_pos
        dist = head_pos.distance_to(target_pos)
        self.score = max(0, 200 / (dist + 1))  # Ajusta o fator de pontuação para maior variação

        # Bônus por chegar perto
        if dist < 50:
            self.score += 50  # Aumenta o bônus para encorajar aproximação
        if dist < 20:
            self.score += 100

        # Penalidade por ficar muito longe
        if dist > 300:
            self.score -= 10  # Penalidade leve para criaturas muito distantes

        try:
            dir_vec = (pygame.Vector2(target_pos) - head_pos)
            if dir_vec.length() > 0:
                dir_norm = dir_vec.normalize()
            else:
                dir_norm = pygame.Vector2(0, 0)

            # Bônus adicional para criaturas que se movem na direção correta
            if dir_norm.y < -0.5:
                self.score += 10  # Incentiva pular
        except Exception:
            pass

    def draw(self, screen):
        if not self.alive:
            return

        color = self.dna['color']

        # Pernas (duas linhas)
        leg_width = 4
        leg_spacing = self.dna['body_size'] * 0.6
        left_leg_x = self.pos.x - leg_spacing / 2
        right_leg_x = self.pos.x + leg_spacing / 2
        leg_bottom_y = self.pos.y
        leg_top_y = self.pos.y - self.dna['leg_length']

        pygame.draw.line(screen, color, (left_leg_x, leg_bottom_y), (left_leg_x, leg_top_y), leg_width)
        pygame.draw.line(screen, color, (right_leg_x, leg_bottom_y), (right_leg_x, leg_top_y), leg_width)

        # Corpo (círculo)
        body_y = self.pos.y - self.dna['leg_length'] - self.dna['body_size']/2
        pygame.draw.circle(screen, color, (int(self.pos.x), int(body_y)), int(self.dna['body_size']/2))

        # Pescoço (linha)
        neck_bottom_y = body_y - self.dna['body_size']/2
        neck_top_y = neck_bottom_y - self.dna['neck_length']
        pygame.draw.line(screen, color, (self.pos.x, neck_bottom_y), (self.pos.x, neck_top_y), 4)

        # Cabeça (círculo menor)
        head_size = 8
        head_pos = self.head_pos
        pygame.draw.circle(screen, color, (int(head_pos.x), int(head_pos.y)), head_size)

        # Olhos
        pygame.draw.circle(screen, (0, 0, 0), (int(head_pos.x - 3), int(head_pos.y - 1)), 2)
        pygame.draw.circle(screen, (0, 0, 0), (int(head_pos.x + 3), int(head_pos.y - 1)), 2)

        # Desenha coroa se for a melhor criatura
        if self.is_best:
            crown_image = pygame.image.load("game/assets/crown.png").convert_alpha()
            crown_image = pygame.transform.scale(crown_image, (30, 30))
            crown_x = int(head_pos.x - 15)  # Centraliza a coroa
            crown_y = int(head_pos.y - 40)  # Posiciona acima da cabeça
            screen.blit(crown_image, (crown_x, crown_y))

        # Desenha retângulo de debug (descomente para ver colisão)
        # pygame.draw.rect(screen, (255, 0, 0), self.get_collision_rect(), 1)
