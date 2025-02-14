import pygame
import random
import math
import time
import matplotlib.pyplot as plt
import threading

# Параметры, которые могут быть изменены пользователем
SCREEN_WIDTH = 800  # Ширина экрана
SCREEN_HEIGHT = 600  # Высота экрана
MAX_ORGANISM_SIZE = 30  # Максимальный размер организма
MUTATION_CHANCE = 0.1  # Вероятность мутации
FOOD_AMOUNT = 20  # Количество пищи, которое организм получает
FOOD_AMOUNT_PER_UPDATE = 5  # Количество пищи, которое появляется в каждом обновлении
INITIAL_ORGANISMS = 100  # Начальное количество организмов
FOOD_SOURCES_COUNT = 150  # Количество источников пищи
TEMPERATURE_RANGE = (-5, 45)  # Диапазон температуры окружающей среды
HUMIDITY_RANGE = (0, 100)  # Диапазон влажности


class Food:
    def __init__(self, x, y, nutrition_value):
        self.x = x
        self.y = y
        self.nutrition_value = nutrition_value  # Питательная ценность пищи


# Класс Организма
class Organism:
    MAX_SIZE = MAX_ORGANISM_SIZE  # Ограничение максимального размера организма

    def __init__(self, x, y, generation=0, shape="circle", can_attack=True, can_eat=True, can_reproduce=True,
                 can_change_color=True, can_change_shape=True, can_eat_offspring=False, can_wander=False,
                 resistance_to_pollution=0.0, color=None, speed=None, size=None, aggression=None):
        self.age = 0  # Возраст организма
        self.x = x
        self.y = y
        self.shape = shape  # Форма организма (круг, квадрат, треугольник и т.д.)
        self.speed = speed if speed is not None else random.uniform(0.5, 2.0)  # Скорость (чем быстрее, тем лучше)
        self.energy = random.uniform(50, 100)  # Энергия (чем больше, тем лучше)
        self.size = size if size is not None else random.uniform(5,
                                                                 20)  # Размер (больше - больше потребности в энергии)

        # Дополнительные характеристики
        if color is None:
            self.color = [random.randint(0, 255) for _ in range(3)]  # Случайный цвет
        else:
            # Унаследуем цвет от родителя с небольшими изменениями
            self.color = [
                max(0, min(255, int(color[0] + random.uniform(-10, 10)))),
                max(0, min(255, int(color[1] + random.uniform(-10, 10)))),
                max(0, min(255, int(color[2] + random.uniform(-10, 10))))
            ]
        self.aggression = aggression if aggression is not None else random.uniform(0, 1)  # Агрессия, шанс атаковать
        self.defense = random.uniform(0, 1)  # Защита, шанс отбиться
        self.eating_range = self.size * 2  # Радиус восприятия пищи зависит от размера
        self.resistance_to_pollution = resistance_to_pollution  # Устойчивость к загрязнению

        # Включение переключателей
        self.can_attack = can_attack
        self.can_eat = can_eat
        self.can_reproduce = can_reproduce
        self.can_change_color = can_change_color
        self.can_change_shape = can_change_shape
        self.can_eat_offspring = can_eat_offspring  # Новый переключатель
        self.can_wander = can_wander  # Новый переключатель для блуждания

        # Параметры поколения
        self.generation = generation  # Номер поколения этого организма

        # Ограничиваем размер организма
        self.size = min(self.size, Organism.MAX_SIZE)

        # Для отслеживания времени бездействия
        self.idle_time = 0

        self.health = 100  # Здоровье организма
        self.experience = 0  # Опыт организма
        self.is_alive = True  # Состояние организма
        self.infected = False  # Статус заражения
        self.memory = []  # Память о нападениях хищников

    def find_food_gradient(self, food_sources):
        # Используем градиентный поиск для нахождения пищи
        if self.can_eat:
            closest_food = None
            max_gradient = -float('inf')

            for food in food_sources:
                distance = math.sqrt((self.x - food.x) ** 2 + (self.y - food.y) ** 2)
                if distance > 0:
                    gradient = self.eating_range / distance  # Градиент, основанный на расстоянии
                    if gradient > max_gradient:
                        max_gradient = gradient
                        closest_food = food

            return closest_food
        return None

    def move(self, width, height, food_sources, organisms):
        # Логика движения
        self.reduce_energy()  # Уменьшаем энергию при движении
        self.age_organism()  # Увеличиваем возраст

        # Проверяем наличие хищников поблизости
        nearby_predators = [org for org in organisms if isinstance(org, Carnivore) and self.can_attack_other(org)]
        if nearby_predators:
            self.avoid_predators(nearby_predators)  # Избегаем хищников
        else:
            # Если хищников нет, ищем пищу
            closest_food = self.find_food_gradient(food_sources)
            if closest_food:
                direction_x = closest_food.x - self.x
                direction_y = closest_food.y - self.y
                distance = math.sqrt(direction_x ** 2 + direction_y ** 2)

                if distance > 0:
                    direction_x /= distance
                    direction_y /= distance
                    self.x += direction_x * self.speed + random.uniform(-0.5, 0.5)
                    self.y += direction_y * self.speed + random.uniform(-0.5, 0.5)

        # Ограничиваем движение организмов, чтобы они не выходили за пределы экрана
        self.x = max(0, min(self.x, width))
        self.y = max(0, min(self.y, height))

    def consume_food(self, food_amount):
        # Поглощение пищи, которая увеличивает энергию и размер
        required_food = self.size * 0.1  # Потребность в пище зависит от размера
        if food_amount >= required_food:
            self.energy += food_amount * 1.5  # Увеличиваем размер пропорционально количеству пищи
            self.size += food_amount * 0.1  # Увеличиваем размер пропорционально количеству пищи
            self.size = min(self.size, Organism.MAX_SIZE)  # Ограничиваем размер
            self.idle_time = 0  # Сброс времени бездействия
        else:
            # Если недостаточно пищи, то только частично восстанавливаем энергию
            self.energy += food_amount * 0.5  # Восстанавливаем меньше энергии

    def reproduce(self):
        if not self.can_reproduce or self.energy < 30:
            return None

        # Генерация характеристик потомка с небольшими вариациями
        child_speed = max(0.1, min(3.0, self.speed + random.uniform(-0.5, 0.5)))
        child_size = max(5, min(Organism.MAX_SIZE, self.size + random.uniform(-1, 1)))
        child_aggression = max(0, min(1, self.aggression + random.uniform(-0.1, 0.1)))

        child = Organism(self.x, self.y, generation=self.generation + 1, shape=self.shape,
                         can_attack=self.can_attack, can_eat=self.can_eat,
                         can_reproduce=self.can_reproduce, can_change_color=self.can_change_color,
                         can_change_shape=self.can_change_shape, can_eat_offspring=self.can_eat_offspring,
                         can_wander=self.can_wander, resistance_to_pollution=self.resistance_to_pollution,
                         color=self.color, speed=child_speed, size=child_size, aggression=child_aggression)

        child.x += random.uniform(-self.size, self.size)
        child.y += random.uniform(-self.size, self.size)

        child.size = self.size * 0.8
        self.size *= 0.9  # Родитель теряет немного размера

        return child

    def is_alive(self):
        # Проверяем, жив ли организм
        return self.energy > 0

    def reduce_energy(self):
        # Увеличиваем затраты энергии в зависимости от состояния
        energy_cost = 0.1  # Базовая стоимость энергии
        if self.age > 50:  # Увеличиваем затраты энергии с возрастом
            energy_cost += 0.05

        # Затраты энергии зависят от уровня энергии
        if self.energy < 20:
            energy_cost += 0.1  # Увеличиваем затраты, если энергия низкая

        self.energy -= energy_cost * self.size * 0.01  # Затраты энергии зависят от размера

    def recover_energy(self, sunlight, food_amount):
        # Восстановление энергии в зависимости от условий
        if sunlight:  # Если есть солнечный свет
            self.energy += 0.1  # Восстанавливаем немного энергии от солнечного света
        if self.can_eat and food_amount > 0:  # Если есть пища
            self.energy += food_amount * 0.5  # Восстанавливаем больше энергии от пищи
        self.energy = min(self.energy, 100)  # Ограничиваем максимальную энергию

    def age_organism(self):
        self.age += 1
        if self.age > 100:  # Организм умирает от старости
            self.reduce_health(1)

    def can_eat_food(self, food):
        # Проверяем, может ли организм съесть пищу на основе расстояния и размера
        if not self.can_eat:
            return False
        distance = math.sqrt((self.x - food[0]) ** 2 + (self.y - food[1]) ** 2)
        return distance < self.eating_range

    def can_attack_other(self, other):
        # Проверяем, может ли организм атаковать другого на основе расстояния и агрессии
        if not self.can_attack:
            return False
        distance = math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)
        return distance < self.size * 2 and random.random() < self.aggression

    def attack(self, other):
        # Логика атаки
        if self.can_attack:
            other.reduce_health(20)  # Наносим урон

    def eat_offspring(self, offspring):
        # Проверяем, может ли организм съесть потомка
        if not self.can_eat_offspring:
            return False
        # Организм может съесть потомка только если тот принадлежит более низкому поколению
        if offspring.generation <= self.generation:  # Если потомок не младше организма
            return False
        distance = math.sqrt((self.x - offspring.x) ** 2 + (self.y - offspring.y) ** 2)
        if distance < self.size:
            self.energy += offspring.energy / 2  # Поглощаем часть энергии
            offspring.energy = 0  # Потомок погибает
            return True
        return False

    def idle_behavior(self):
        # В этом случае, нам нужно передать пустой список или реальные источники пищи
        self.move(SCREEN_WIDTH, SCREEN_HEIGHT, [],
                  [])  # Двигаемся случайным образом, передаем пустой список, если пищи нет

    def draw(self, screen):
        # Создаем полупрозрачную оболочку
        size = max(1, min(self.size * 3, 1000))  # Ограничиваем размер
        glow_surface = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (*self.color, 50), (size // 2, size // 2), self.size * 1.5)
        screen.blit(glow_surface, (self.x - size // 2, self.y - size // 2))  # Рисуем оболочку

        # Рисуем сам организм
        if self.is_alive:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(self.size))

    def mutate(self):
        if random.random() < MUTATION_CHANCE:  # Шанс на мутацию
            mutation_type = random.choice(['size', 'speed', 'aggression', 'defense', 'toxin_absorption'])
            if mutation_type == 'size':
                change = random.uniform(-1, 1)
                self.size = max(5, min(self.size + change, Organism.MAX_SIZE))
            elif mutation_type == 'speed':
                change = random.uniform(-0.5, 0.5)
                self.speed = max(0.1, self.speed + change)
            elif mutation_type == 'aggression':
                change = random.uniform(-0.1, 0.1)
                self.aggression = max(0, min(self.aggression + change, 1))
            elif mutation_type == 'defense':
                change = random.uniform(-0.1, 0.1)
                self.defense = max(0, min(self.defense + change, 1))
            elif mutation_type == 'toxin_absorption':
                self.can_absorb_toxins = True  # Уникальная способность поглощать токсины

    def adjust_to_environment(self, temperature, humidity):
        # Воздействие температуры и влажности
        if temperature > 35:
            self.energy -= 0.1
            self.speed -= 0.05
        elif temperature < 5:
            self.energy -= 0.2
            self.speed -= 0.1

        if humidity < 30:
            self.energy -= 0.05
        elif humidity > 70:
            self.energy -= 0.05

        # Воздействие загрязнения
        if self.resistance_to_pollution < 1.0:  # Если организм не полностью устойчив к загрязнению
            pollution_effect = 1.0 - self.resistance_to_pollution
            self.reduce_health(pollution_effect * 5)  # Уменьшаем здоровье в зависимости от загрязнения

        # Проверка на заражение
        if self.infected:
            self.energy -= 0.2  # Снижаем энергию, если организм заражен
            self.age += 1  # Увеличиваем возраст быстрее
            if self.age > 100:  # Умирает от старости
                self.reduce_health(1)

        self.mutate()  # Вызываем мутацию

    def social_behavior(self, organisms):
        # Проверяем, есть ли другие организмы рядом
        nearby_organisms = [org for org in organisms if org != self and self.can_attack_other(org)]
        if nearby_organisms:
            # Двигаемся к центру группы
            avg_x = sum(org.x for org in nearby_organisms) / len(nearby_organisms)
            avg_y = sum(org.y for org in nearby_organisms) / len(nearby_organisms)
            direction_x = avg_x - self.x
            direction_y = avg_y - self.y
            distance = math.sqrt(direction_x ** 2 + direction_y ** 2)

            if distance > 0:
                direction_x /= distance
                direction_y /= distance
                self.x += direction_x * self.speed * 0.5  # Двигаемся к центру группы
                self.y += direction_y * self.speed * 0.5

    def learn(self):
        # Логика обучения, например, увеличение скорости или агрессии
        if self.can_attack:
            self.aggression = min(1, self.aggression + 0.05)  # Увеличиваем агрессию
        else:
            self.speed = min(3.0, self.speed + 0.1)  # Увеличиваем скорость

        self.experience += 1  # Увеличиваем опыт

    def reduce_health(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.is_alive = False  # Организм умирает
            self.color = [max(0, c - 50) for c in self.color]  # Темнее цвет при смерти
            self.energy = 0  # Организм погибает

    def check_infection(self, nearby_organisms):
        for organism in nearby_organisms:
            if organism.infected and random.random() < 0.1:  # 10% шанс на заражение
                self.infected = True

    def learn_from_encounter(self, predator):
        # Запоминаем встречу с хищником
        self.memory.append(predator)

    def avoid_predators(self, predators):
        # Если есть память о хищниках, избегаем их
        for predator in predators:
            if predator in self.memory:
                # Избегаем хищника
                direction_x = self.x - predator.x
                direction_y = self.y - predator.y
                distance = math.sqrt(direction_x ** 2 + direction_y ** 2)

                if distance > 0:
                    direction_x /= distance
                    direction_y /= distance
                    self.x += direction_x * self.speed * 0.5
                    self.y += direction_y * self.speed * 0.5


class Herbivore(Organism):
    def __init__(self, x, y, generation=0):
        super().__init__(x, y, generation=generation, shape="circle", can_attack=False, can_eat=True)
        self.resistance_to_pollution = 0.2  # Травоядные хуже переносят загрязнение
        self.flock = []  # Список для хранения членов стаи

    def move(self, width, height, food_sources, organisms):
        super().move(width, height, food_sources, organisms)

        # Логика формирования стаи
        nearby_herbivores = [org for org in organisms if isinstance(org, Herbivore) and org.is_alive and org != self]
        if nearby_herbivores:
            # Собираемся в стаю
            for herbivore in nearby_herbivores:
                if self.distance_to(herbivore) < 50:  # Если травоядные близко друг к другу
                    self.flock.append(herbivore)

            # Двигаемся к центру стаи
            if self.flock:
                avg_x = sum(member.x for member in self.flock) / len(self.flock)
                avg_y = sum(member.y for member in self.flock) / len(self.flock)
                direction_x = avg_x - self.x
                direction_y = avg_y - self.y
                distance = math.sqrt(direction_x ** 2 + direction_y ** 2)

                if distance > 0:
                    direction_x /= distance
                    direction_y /= distance
                    self.x += direction_x * self.speed * 0.5  # Двигаемся к центру стаи
                    self.y += direction_y * self.speed * 0.5

        # Ограничиваем движение организмов, чтобы они не выходили за пределы экрана
        self.x = max(0, min(self.x, width))
        self.y = max(0, min(self.y, height))

    def distance_to(self, other):
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

    def idle_behavior(self):
        # Логика бездействия, если нет пищи
        if not self.flock:
            self.move(SCREEN_WIDTH, SCREEN_HEIGHT, [], [])  # Двигаемся случайным образом, если нет стаи

    def reproduce(self):
        # Увеличиваем вероятность размножения, если уровень энергии высокий
        if not self.can_reproduce or self.energy < 30:
            return None

        # Увеличиваем вероятность размножения, если энергия выше 70
        if self.energy > 70 and random.random() < 0.2:  # 20% шанс на размножение
            child = Organism(self.x, self.y, generation=self.generation + 1, shape=self.shape,
                             can_attack=self.can_attack, can_eat=self.can_eat,
                             can_reproduce=self.can_reproduce, can_change_color=self.can_change_color,
                             can_change_shape=self.can_change_shape, can_eat_offspring=self.can_eat_offspring,
                             can_wander=self.can_wander, resistance_to_pollution=self.resistance_to_pollution)

            child.x += random.uniform(-self.size, self.size)
            child.y += random.uniform(-self.size, self.size)

            child.size = self.size * 0.8
            self.size *= 0.9  # Родитель теряет немного размера

            return child

        # Если энергия ниже 70, вероятность размножения обычная
        return super().reproduce()


class Carnivore(Organism):
    def __init__(self, x, y, generation=0):
        super().__init__(x, y, generation=generation, shape="circle", can_attack=True, can_eat=True)
        self.resistance_to_pollution = 0.3  # Хищники имеют среднюю устойчивость к загрязнению

    def move(self, width, height, food_sources, organisms):
        super().move(width, height, food_sources, organisms)

        # Логика атаки
        vulnerable_prey = None
        min_health = float('inf')

        for organism in organisms:
            if isinstance(organism, (Herbivore, Omnivore)) and organism.is_alive:
                # Выбираем наиболее уязвимого
                if organism.health < min_health:
                    min_health = organism.health
                    vulnerable_prey = organism

        if vulnerable_prey:
            # Двигаемся к наиболее уязвимой жертве
            direction_x = vulnerable_prey.x - self.x
            direction_y = vulnerable_prey.y - self.y
            distance = math.sqrt(direction_x ** 2 + direction_y ** 2)

            if distance > 0:
                direction_x /= distance
                direction_y /= distance
                self.x += direction_x * self.speed + random.uniform(-0.5, 0.5)
                self.y += direction_y * self.speed + random.uniform(-0.5, 0.5)

            # Атакуем, если находимся достаточно близко
            if distance < self.size * 2:
                self.attack(vulnerable_prey)
                vulnerable_prey.learn_from_encounter(self)  # Запоминаем встречу с хищником


class Omnivore(Organism):
    def __init__(self, x, y, generation=0):
        super().__init__(x, y, generation=generation, shape="circle", can_attack=True, can_eat=True)

    def move(self, width, height, food_sources, organisms):
        # Логика движения всеядного
        closest_food = self.find_food_gradient(food_sources)
        if closest_food:
            direction_x = closest_food.x - self.x
            direction_y = closest_food.y - self.y
            distance = math.sqrt(direction_x ** 2 + direction_y ** 2)

            if distance > 0:
                direction_x /= distance
                direction_y /= distance
                self.x += direction_x * self.speed + random.uniform(-0.5, 0.5)
                self.y += direction_y * self.speed + random.uniform(-0.5, 0.5)

        for organism in organisms:
            if self.can_attack_other(organism):
                self.attack(organism)


class Autotroph(Organism):
    def __init__(self, x, y, generation=0, type="phototroph"):
        super().__init__(x, y, generation=generation, shape="circle", can_attack=False, can_eat=False)
        self.type = type
        self.resistance_to_pollution = 0.5  # Автотрофы лучше переносят загрязнение

    def produce_energy(self):
        if self.type == "phototroph":
            self.energy += 5  # Получаем энергию от света
        elif self.type == "chemotroph":
            self.energy += 3  # Получаем энергию от химических реакций

    def move(self, width, height, food_sources, organisms):
        # Автотрофы не ищут пищу, но могут перемещаться
        self.produce_energy()  # Производим энергию
        super().move(width, height, food_sources, organisms)


class FilterFeeder(Organism):
    def __init__(self, x, y, generation=0):
        super().__init__(x, y, generation=generation, shape="circle", can_attack=False, can_eat=True)

    def find_food(self, water_sources):
        # Логика поиска пищи в воде
        for water in water_sources:
            if self.can_eat:
                self.consume_food(FOOD_AMOUNT)  # Поглощаем пищу


class Parasite(Organism):
    def __init__(self, x, y, generation=0):
        super().__init__(x, y, generation=generation, shape="circle", can_attack=True, can_eat=False)

    def attack(self, host):
        # Логика атаки на хозяина
        if self.can_attack:
            host.reduce_health(10)  # Наносим урон хозяину
            self.energy += 5  # Получаем энергию от хозяина

            # Проверяем, не погиб ли хозяин
            if not host.is_alive:
                self.is_alive = False  # Паразит погибает вместе с хозяином


class SymbioticOrganism(Organism):
    def __init__(self, x, y, generation=0):
        super().__init__(x, y, generation=generation, shape="circle", can_attack=False, can_eat=True)

    def interact(self, partner):
        # Логика симбиотического взаимодействия
        if isinstance(partner, SymbioticOrganism):
            self.energy += 2  # Получаем небольшую выгоду от партнера
            partner.energy += 2  # Партнер также получает выгоду


class Detritivore(Organism):
    def __init__(self, x, y, generation=0):
        super().__init__(x, y, generation=generation, shape="circle", can_attack=False, can_eat=True)
        self.resistance_to_pollution = 0.3  # Устойчивость к загрязнению

    def move(self, width, height, organisms):
        # Логика движения детритофага
        self.reduce_energy()  # Уменьшаем энергию при движении
        self.age_organism()  # Увеличиваем возраст

        # Ищем мертвые организмы для переработки
        dead_organisms = [org for org in organisms if not org.is_alive]
        if dead_organisms:
            closest_dead = min(dead_organisms, key=lambda org: self.distance_to(org))
            direction_x = closest_dead.x - self.x
            direction_y = closest_dead.y - self.y
            distance = math.sqrt(direction_x ** 2 + direction_y ** 2)

            if distance > 0:
                direction_x /= distance
                direction_y /= distance
                self.x += direction_x * self.speed + random.uniform(-0.5, 0.5)
                self.y += direction_y * self.speed + random.uniform(-0.5, 0.5)

            # Если достаточно близко, перерабатываем мертвый организм
            if distance < self.size * 2:
                self.consume_food(10)  # Получаем пищу от переработки
                dead_organisms.remove(closest_dead)  # Удаляем переработанный организм

        # Ограничиваем движение организмов, чтобы они не выходили за пределы экрана
        self.x = max(0, min(self.x, width))
        self.y = max(0, min(self.y, height))


# Класс Среды
class Environment:
    def __init__(self, width, height, num_organisms, settings):
        self.width = width
        self.height = height
        self.max_organisms = num_organisms
        self.organisms = [Herbivore(random.randint(0, width), random.randint(0, height)) for _ in
                          range(num_organisms // 3)] + \
                         [Carnivore(random.randint(0, width), random.randint(0, height)) for _ in
                          range(num_organisms // 3)] + \
                         [Omnivore(random.randint(0, width), random.randint(0, height)) for _ in
                          range(num_organisms // 3)]
        # Остальные организмы могут быть обычными
        self.organisms += [Organism(random.randint(0, width), random.randint(0, height), **settings) for _ in
                           range(num_organisms // 3)]
        self.food_sources = [Food(random.randint(0, width), random.randint(0, height), random.uniform(5, 20)) for _ in
                             range(FOOD_SOURCES_COUNT)]
        self.dead_organisms = []  # Список мертвых организмов
        self.pollution = 0  # Загрязнение окружающей среды
        self.temperature = random.uniform(*TEMPERATURE_RANGE)  # Температура окружающей среды (-5 до 45°C)
        self.co2_level = 100  # Уровень CO₂ в среде (по умолчанию)
        self.population_data = []  # Данные о популяции
        self.pollution_data = []  # Данные о загрязнении
        self.temperature_data = []  # Данные о температуре
        self.time = 0  # Время симуляции
        self.running = True  # Флаг для управления потоком
        self.show_graphs = False  # Флаг для отображения графиков

    def update(self):
        # Обновление состояния всех организмов
        self.time += 1  # Увеличиваем время
        if self.time % 1000 == 0:
            self.pollution += 1  # Загрязнение увеличивается с каждым тактом времени
            self.pollution = min(self.pollution, 100)  # Максимум загрязнения

        # Случайные события
        if random.random() < 0.01:  # 1% шанс на случайное событие
            self.temperature += random.uniform(-5, 5)  # Изменение температуры
            self.co2_level += random.uniform(-10, 10)  # Изменение уровня CO₂

        self.temperature = max(-5, min(self.temperature, 45))  # Ограничиваем диапазон температуры
        self.co2_level = max(0, min(self.co2_level, 100))  # Ограничиваем диапазон уровня CO₂

        # Воссоздаем источники пищи
        if len(self.food_sources) < 50:  # Если пищи меньше 50, добавляем новые источники
            for _ in range(FOOD_AMOUNT_PER_UPDATE):
                self.food_sources.append(
                    Food(random.randint(0, self.width), random.randint(0, self.height), random.uniform(5, 20)))

        # Обновляем всех организмов
        for organism in self.organisms:
            organism.move(self.width, self.height, self.food_sources, self.organisms)
            organism.reduce_energy()

            # Влияние окружающей среды на организм
            organism.adjust_to_environment(self.temperature, self.co2_level)

            # Проверяем, мертв ли организм
            if not organism.is_alive:
                self.dead_organisms.append(organism)  # Добавляем мертвый организм в список

            for food in self.food_sources:
                if organism.can_eat_food((food.x, food.y)):
                    organism.consume_food(food.nutrition_value)  # Используем питательную ценность пищи
                    self.food_sources.remove(food)
                    break

            organism.idle_behavior()

        # Конкуренция за ресурсы
        for i, organism in enumerate(self.organisms):
            for j, other in enumerate(self.organisms):
                if i != j and organism.can_attack_other(other):
                    if organism.attack(other):
                        break  # Если атакующий съел другого, он прекращает атаку

        # Убираем мертвых организмы из списка
        self.organisms = [org for org in self.organisms if org.is_alive]

        # Размножение
        new_organisms = []
        for organism in self.organisms:
            if organism.energy > 30 and random.random() < 0.1:  # вероятность размножения увеличена и проверка энергии
                new_organisms.append(organism.reproduce())

        self.organisms.extend(new_organisms)

        # Поедание потомков
        for organism in self.organisms:
            if organism.can_eat_offspring:
                for offspring in self.organisms:
                    if offspring != organism:
                        organism.eat_offspring(offspring)

        # Ограничиваем количество организмов
        if len(self.organisms) > self.max_organisms:
            self.organisms = self.organisms[:self.max_organisms]

        # Восстановление энергии для всех организмов
        for organism in self.organisms:
            if organism.is_alive:
                # Проверяем наличие солнечного света (например, случайно)
                sunlight = random.random() < 0.5  # 50% шанс на наличие солнечного света
                food_amount = len(self.food_sources)  # Количество доступной пищи
                organism.recover_energy(sunlight, food_amount)  # Восстанавливаем энергию

        # Сохраняем данные для графиков
        self.population_data.append(len(self.organisms))
        self.pollution_data.append(self.pollution)
        self.temperature_data.append(self.temperature)

    def draw(self, screen):
        # Рисуем градиентный фон
        draw_gradient_background(screen, self.width, self.height)

        # Отображаем источники пищи
        for food in self.food_sources:
            glow_surface = pygame.Surface((10, 10), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (0, 255, 0, 100), (5, 5), 5)
            screen.blit(glow_surface, (food.x - 5, food.y - 5))
            pygame.draw.circle(screen, (0, 255, 0), (food.x, food.y), 3)

        # Отображаем организмы
        for organism in self.organisms:
            organism.draw(screen)

    def draw_graphs(self):
        plt.ion()  # Включаем интерактивный режим
        while self.running:
            if self.show_graphs:
                plt.clf()  # Очищаем текущее окно графиков

                # График численности видов
                plt.subplot(3, 1, 1)
                plt.plot(self.population_data, label='Population Size', color='blue')
                plt.title('Population Size Over Time')
                plt.xlabel('Time Steps')
                plt.ylabel('Population Size')
                plt.legend()

                # График загрязнения
                plt.subplot(3, 1, 2)
                plt.plot(self.pollution_data, label='Pollution Level', color='green')
                plt.title('Pollution Level Over Time')
                plt.xlabel('Time Steps')
                plt.ylabel('Pollution Level')
                plt.legend()

                # График температуры
                plt.subplot(3, 1, 3)
                plt.plot(self.temperature_data, label='Temperature', color='red')
                plt.title('Temperature Over Time')
                plt.xlabel('Time Steps')
                plt.ylabel('Temperature')
                plt.legend()

                plt.tight_layout()
                plt.pause(1)  # Обновляем графики каждую секунду


# Основной цикл симуляции с Pygame
def draw_gradient_background(screen, width, height):
    # Цвета для градиента (от светло-голубого к глубокому синему)
    start_color = (135, 206, 235)  # Светло-голубой (небо)
    end_color = (0, 0, 139)  # Темно-синий (глубокий океан или ночное небо)

    # Для вертикального градиента
    for y in range(height):
        # Пропорция на основе позиции по оси Y
        ratio = y / height
        # Линейное интерполирование для каждого канала (RGB)
        r = int(start_color[0] * (1 - ratio) + end_color[0] * ratio)
        g = int(start_color[1] * (1 - ratio) + end_color[1] * ratio)
        b = int(start_color[2] * (1 - ratio) + end_color[2] * ratio)
        # Рисуем линию с этим цветом
        pygame.draw.line(screen, (r, g, b), (0, y), (width, y))


# Основной цикл симуляции с добавлением градиентного фона
def draw_water_shimmering_background(screen, width, height, time):
    color1 = (70, 130, 180)
    color2 = (0, 206, 209)
    color3 = (32, 178, 170)

    speed = 0.002
    r = int(127.5 * (math.sin(time * speed) + 1))
    g = int(127.5 * (math.sin(time * speed + math.pi / 3) + 1))
    b = int(127.5 * (math.sin(time * speed + 2 * math.pi / 3) + 1))

    for y in range(height):
        ratio = y / height
        interpolated_r = int(r * (1 - ratio) + color1[0] * ratio)
        interpolated_g = int(g * (1 - ratio) + color2[1] * ratio)
        interpolated_b = int(b * (1 - ratio) + color3[2] * ratio)

        pygame.draw.line(screen, (interpolated_r, interpolated_g, interpolated_b), (0, y), (width, y))


def run_simulation():
    # Инициализация Pygame
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Эволюционный симулятор одноклеточных организмов')

    settings = {
        'shape': 'circle',
        'can_attack': True,
        'can_eat': True,
        'can_reproduce': True,
        'can_change_color': True,
        'can_change_shape': False,
        'can_eat_offspring': True,
        'can_wander': True
    }

    env = Environment(SCREEN_WIDTH, SCREEN_HEIGHT, INITIAL_ORGANISMS, settings)

    # Запускаем поток для рисования графиков
    graph_thread = threading.Thread(target=env.draw_graphs)
    graph_thread.start()

    running = True
    time = 0
    simulation_speed = 50  # Начальная скорость симуляции

    while running:
        draw_gradient_background(screen, SCREEN_WIDTH, SCREEN_HEIGHT)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:  # Увеличение скорости
                    simulation_speed = max(10, simulation_speed - 10)  # Увеличиваем скорость
                elif event.key == pygame.K_DOWN:  # Уменьшение скорости
                    simulation_speed += 10  # Уменьшаем скорость
                elif event.key == pygame.K_g:  # Нажмите 'G' для отображения графиков
                    env.show_graphs = not env.show_graphs  # Переключаем отображение графиков

        env.update()
        env.draw(screen)
        pygame.display.flip()
        time += 1
        pygame.time.delay(simulation_speed)  # Используем переменную скорости

        # Проверка на гибель всех организмов
        if len(env.organisms) == 0:
            running = False
            show_game_over_screen(screen, time)

    env.running = False  # Останавливаем поток перед выходом
    graph_thread.join()  # Ждем завершения потока

    pygame.quit()


def show_game_over_screen(screen, total_time):
    # Преобразуем общее время в часы, минуты и секунды
    seconds = total_time // 1000
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60

    # Создаем текст сообщения
    font = pygame.font.Font(None, 74)
    text = font.render("Все одноклеточные погибли!", True, (255, 0, 0))
    time_text = font.render(f"Время симуляции: {hours:02}:{minutes:02}:{seconds:02}", True, (255, 255, 255))
    restart_text = font.render("Нажмите R для перезапуска или Q для выхода", True, (255, 255, 255))

    # Отображаем текст на экране
    screen.fill((0, 0, 0))  # Черный фон
    screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - 100))
    screen.blit(time_text, (SCREEN_WIDTH // 2 - time_text.get_width() // 2, SCREEN_HEIGHT // 2))
    screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 100))
    pygame.display.flip()

    # Ожидание ввода пользователя
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:  # Перезапуск
                    run_simulation()
                elif event.key == pygame.K_q:  # Выход
                    waiting = False


# Запуск симуляции
run_simulation()
