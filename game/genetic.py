import random
from components.creature import Creature

class GeneticAlgorithm:
    def __init__(self, population_size=20):
        self.population_size = population_size
        self.generation = 1
        self.best_fitness_history = []
        self.mutation_rate = 0.05
        
    def create_population(self, x, y):
        """Cria população inicial com DNA aleatório"""
        population = []
        for i in range(self.population_size):
            # Espalha as criaturas horizontalmente
            spawn_x = x + (i - self.population_size // 2) * 30
            population.append(Creature(spawn_x, y))
        return population
    
    def evaluate_fitness(self, population):
        """Calcula e normaliza fitness de toda população"""
        total_fitness = sum(c.score for c in population)
        if total_fitness == 0:
            return [1.0 / len(population)] * len(population)
        
        # Normaliza fitness entre 0 e 1
        return [c.score / total_fitness for c in population]
    
    def selection(self, population, fitness_scores):
        """Seleção por torneio - escolhe os melhores indivíduos"""
        tournament_size = 3
        selected = []
        
        for _ in range(self.population_size):
            # Escolhe 3 indivíduos aleatórios
            tournament_indices = random.sample(range(len(population)), tournament_size)
            tournament = [(population[i], fitness_scores[i]) for i in tournament_indices]
            
            # Seleciona o melhor do torneio
            winner = max(tournament, key=lambda x: x[1])[0]
            selected.append(winner)
        
        return selected
    
    def crossover(self, parent1, parent2):
        """Combina DNA de dois pais para criar filho"""
        child_dna = {}
        
        # Para cada gene, escolhe aleatoriamente de um dos pais ou faz média
        for gene in parent1.dna:
            if random.random() < 0.5:
                # Pega do pai 1
                child_dna[gene] = parent1.dna[gene]
            else:
                # Pega do pai 2
                child_dna[gene] = parent2.dna[gene]
            
            # Às vezes faz média dos dois pais
            if random.random() < 0.3 and gene != 'color':
                if isinstance(parent1.dna[gene], (int, float)):
                    child_dna[gene] = (parent1.dna[gene] + parent2.dna[gene]) / 2
        
        return child_dna
    
    def mutate(self, dna):
        """Aplica mutações aleatórias no DNA"""
        mutated_dna = dna.copy()
        
        # Mutação no comprimento das pernas
        if random.random() < self.mutation_rate:
            # mutated_dna['leg_length'] = max(20, min(60, 
            #     mutated_dna['leg_length'] + random.uniform(-10, 10)))
        
            mutated_dna['leg_length'] = max(20, (60 - mutated_dna['body_size'])) #sem controle
        
        # Mutação no comprimento do pescoço
        if random.random() < self.mutation_rate:
            # mutated_dna['neck_length'] = max(15, min(80, 
            #     mutated_dna['neck_length'] + random.uniform(-15, 15)))

            mutated_dna['neck_length'] = max(15, (80 - mutated_dna['leg_length'])) #sem controle
        
        # Mutação no tamanho do corpo
        if random.random() < self.mutation_rate:
            # mutated_dna['body_size'] = max(15, min(35, 
            #     mutated_dna['body_size'] + random.uniform(-5, 5)))

            mutated_dna['body_size'] = max(15, (35 - mutated_dna['leg_length'])) #sem controle
        
        # Mutação na força do pulo
        if random.random() < self.mutation_rate:
            # mutated_dna['jump_strength'] = max(8, min(18, 
            #     mutated_dna['jump_strength'] + random.uniform(-3, 3)))

            mutated_dna['jump_strength'] = max(8, (18 - mutated_dna['body_size'])) #sem controle
        

        # Mutação no timing do pulo
        if random.random() < self.mutation_rate:
            # mutated_dna['jump_timing'] = max(0.5, min(3.0, 
            #     mutated_dna['jump_timing'] + random.uniform(-0.5, 0.5)))

            mutated_dna['jump_timing'] = max(0.5, (3.0 - mutated_dna['body_size'])) #sem controle

        # Mutação na cor
        if random.random() < self.mutation_rate:
            r, g, b = mutated_dna['color']
            mutated_dna['color'] = (
                max(0, min(255, r + random.randint(-30, 30))),
                max(0, min(255, g + random.randint(-30, 30))),
                max(0, min(255, b + random.randint(-30, 30)))
            )
        
        return mutated_dna
    
    def evolve(self, population, spawn_x, spawn_y):
        """Evolui a população para a próxima geração"""
        # Avalia fitness
        fitness_scores = self.evaluate_fitness(population)
        
        # Guarda o melhor fitness
        best_score = max(c.score for c in population)
        self.best_fitness_history.append(best_score)
        
        # Ordena população por fitness
        sorted_pop = sorted(zip(population, fitness_scores), key=lambda x: x[1], reverse=True)
        population = [p[0] for p in sorted_pop]
        fitness_scores = [f[1] for f in sorted_pop]
        
        # Nova população
        new_population = []
        
        # Elitismo: mantém os 2 melhores
        elite_count = 2
        for i in range(elite_count):
            new_creature = Creature(spawn_x + (i - elite_count // 2) * 30, spawn_y, 
                                   population[i].dna.copy())
            new_population.append(new_creature)
        
        # Seleciona pais e cria filhos
        parents = self.selection(population, fitness_scores)
        
        for i in range(elite_count, self.population_size):
            # Escolhe dois pais aleatórios
            parent1 = random.choice(parents)
            parent2 = random.choice(parents)
            
            # Crossover
            child_dna = self.crossover(parent1, parent2)
            
            # Mutação
            child_dna = self.mutate(child_dna)
            
            # Cria nova criatura
            spawn_offset = (i - self.population_size // 2) * 30
            new_creature = Creature(spawn_x + spawn_offset, spawn_y, child_dna)
            new_population.append(new_creature)
        
        self.generation += 1
        return new_population
    
    def get_best_creature(self, population):
        """Retorna a melhor criatura da população"""
        return max(population, key=lambda c: c.score)
    
    def get_statistics(self, population):
        """Retorna estatísticas da população atual"""
        scores = [c.score for c in population]
        return {
            'best': max(scores) if scores else 0,
            'worst': min(scores) if scores else 0,
            'average': sum(scores) / len(scores) if scores else 0,
            'median': sorted(scores)[len(scores) // 2] if scores else 0
        }
