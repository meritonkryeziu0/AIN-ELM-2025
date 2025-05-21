import random


class GeneticAlgorithm:
    def __init__(self, population_size, chromosome_length, fitness_fn,
                 crossover_rate=0.8, mutation_rate=0.02, tournament_size=3, generations=100,
                 initial_population=None):
        self.population_size = population_size
        self.chromosome_length = chromosome_length
        self.fitness_fn = fitness_fn
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.tournament_size = tournament_size
        self.generations = generations
        self.initial_population = initial_population

    def initialize_population(self):
        population = []
        if self.initial_population:
            # If initial_population is a list of solutions, use it directly
            if isinstance(self.initial_population[0], list):
                population.extend(self.initial_population)
            else:
                # If initial_population is a single solution, wrap it in a list
                population.append(self.initial_population)

        # Fill the rest of the population with random individuals
        while len(population) < self.population_size:
            individual = [random.randint(0, 1) for _ in range(self.chromosome_length)]
            population.append(individual)
        return population

    def tournament_selection(self, population, fitnesses):
        selected = random.sample(list(zip(population, fitnesses)), self.tournament_size)
        return max(selected, key=lambda x: x[1])[0]

    def crossover(self, parent1, parent2):
        if random.random() < self.crossover_rate:
            point = random.randint(1, self.chromosome_length - 1)
            return parent1[:point] + parent2[point:]
        return parent1[:], parent2[:]

    def mutate(self, chromosome):
        return [gene if random.random() > self.mutation_rate else 1 - gene for gene in chromosome]

    def run(self):
        population = self.initialize_population()
        for gen in range(self.generations):
            fitnesses = [self.fitness_fn(ind) for ind in population]
            new_population = []
            while len(new_population) < self.population_size:
                parent1 = self.tournament_selection(population, fitnesses)
                parent2 = self.tournament_selection(population, fitnesses)
                child1, child2 = self.crossover(parent1, parent2)
                new_population.append(self.mutate(child1))
                if len(new_population) < self.population_size:
                    new_population.append(self.mutate(child2))
            population = new_population
            print(f"Generation {gen}: Best fitness = {max(fitnesses)}")
        # Return the best solution
        best_idx = fitnesses.index(max(fitnesses))
        return population[best_idx], max(fitnesses)
