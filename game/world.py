"""
Over arching world function, soldiers interact with it and each other through this.
"""
from game.soldier import Soldier
from game.helper import *
import pygame
import math
import sys

pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
CIRCLE_RADIUS = 20
PROJECTILE_RADIUS = 5
WALL_SIZE = 50

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (200, 200, 200)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)

# Circle properties
rotation_speed = math.radians(2)
circle_speed = 1

# Projectile properties
projectile_speed = 50


class World:
    def __init__(self):
        self.soldiers = []
        self.projectiles = []

        self.walls = []
        level_data = load_level("level.txt")
        for wall_y in range(len(level_data)):
            for wall_x in range(len(level_data[wall_y])):
                cell = level_data[wall_y][wall_x]
                if cell == "#":
                    self.walls.append(pygame.Rect(wall_x * WALL_SIZE, wall_y * WALL_SIZE, WALL_SIZE, WALL_SIZE))
                elif cell == "B":
                    self.soldiers.append(Soldier(self, wall_x * WALL_SIZE, wall_y * WALL_SIZE, team="Blue"))
                elif cell == "R":
                    self.soldiers.append(Soldier(self, wall_x * WALL_SIZE, wall_y * WALL_SIZE, team="Red"))

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pass

    def draw(self):
        self.screen.fill(WHITE)

        for soldier in self.soldiers:
            pygame.draw.circle(self.screen, soldier.color, (soldier.x, soldier.y), CIRCLE_RADIUS)

            direction_indicator_x = soldier.x + CIRCLE_RADIUS * math.cos(soldier.angle)
            direction_indicator_y = soldier.y - CIRCLE_RADIUS * math.sin(soldier.angle)
            pygame.draw.line(self.screen, BLACK, (soldier.x, soldier.y),
                             (direction_indicator_x, direction_indicator_y), 2)

        for projectile in self.projectiles:
            projectile_x, projectile_y, _ = projectile
            pygame.draw.circle(self.screen, RED, (int(projectile_x), int(projectile_y)), PROJECTILE_RADIUS)

        for wall in self.walls:
            pygame.draw.rect(self.screen, GRAY, wall)

        pygame.display.flip()

    def next_tick(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Update projectile positions
        to_be_deleted = []
        for i in range(len(self.projectiles)):
            projectile_x, projectile_y, projectile_angle = self.projectiles[i]
            projectile_x += projectile_speed * math.cos(projectile_angle)
            projectile_y -= projectile_speed * math.sin(projectile_angle)

            if not 0 < projectile_x < WIDTH:
                to_be_deleted.append(i)
                continue
            if not 0 < projectile_y < HEIGHT:
                to_be_deleted.append(i)
                continue

            if any(wall.collidepoint(projectile_x, projectile_y) for wall in self.walls):
                to_be_deleted.append(i)
                continue

            self.projectiles[i] = (projectile_x, projectile_y, projectile_angle)

            for soldier in self.soldiers:
                if math.hypot(projectile_x - soldier.x, projectile_y - soldier.y) <= CIRCLE_RADIUS:
                    soldier.death = True
                    soldier.color = BLACK
                    to_be_deleted.append(i)

        to_be_deleted.reverse()
        for i in to_be_deleted:
            del self.projectiles[i]

        self.draw()

    def move(self, soldier, direction):
        x = soldier.x
        y = soldier.y

        if direction == "up":
            y -= circle_speed
        elif direction == "down":
            y += circle_speed
        elif direction == "left":
            x -= circle_speed
        elif direction == "right":
            x += circle_speed

        # We could probably do something fancier, like retrying the attempt until its flush with the wall. But with a
        # soldier speed of 1 this is functionally equivalent and slightly optimized.
        for wall in self.walls:
            if check_wall_collisions((x, y), CIRCLE_RADIUS,
                                     wall.center, wall.width, wall.height):
                x = soldier.x
                y = soldier.y
                return x, y

        for soldier2 in self.soldiers:
            if soldier == soldier2:
                continue

            distance = math.sqrt((x - soldier2.x) ** 2 + (y - soldier2.y) ** 2)
            if distance < 2 * CIRCLE_RADIUS:
                overlap_distance = 2 * CIRCLE_RADIUS - distance
                if x <= soldier2.x:
                    x -= overlap_distance
                else:
                    x += overlap_distance

                if y <= soldier2.y:
                    y -= overlap_distance
                else:
                    y += overlap_distance

        # Keep the circle within the screen bounds
        x = max(CIRCLE_RADIUS, min(WIDTH - CIRCLE_RADIUS, x))
        y = max(CIRCLE_RADIUS, min(HEIGHT - CIRCLE_RADIUS, y))

        return x, y

    @staticmethod
    def rotate(soldier, direction):
        angle = soldier.angle
        if direction == "clockwise":
            angle -= rotation_speed
        if direction == "counter_clockwise":
            angle += rotation_speed

        return angle

    def get_vision(self, soldier):
        # Let's be naive, and only say we can see an object when there is a straight line between the center's
        visible = []
        for wall in self.walls:
            if not check_intersections(wall.center, (soldier.x, soldier.y), self, world_object=wall,
                                       soldier=soldier):
                visible.append(wall)

        for soldier2 in self.soldiers:
            if soldier2 == soldier:
                continue
            if not check_intersections((soldier2.x, soldier2.y), (soldier.x, soldier.y), self,
                                       world_object=soldier2, soldier=soldier):
                visible.append(soldier2)

        return visible

    def shoot(self, soldier):
        self.projectiles.append((soldier.x, soldier.y, soldier.angle))
