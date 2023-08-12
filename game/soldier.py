"""
Simple soldier class

This also provides the interface for a network to interact with, this means it needs to expose the following:
- Location (x, y)
- Orientation (degrees)
- Vision (walls, friendlies, hostiles)

- move (left, right, up, down)
- rotate (left, right)
- shoot
"""
import game.world as w


class Soldier:
    def __init__(self, world, x, y, angle=1, team="Blue"):
        self.x = x
        self.y = y
        self.angle = angle

        self.team = team
        self.death = False

        if team == "Blue":
            self.color = w.BLUE
        else:
            self.color = w.RED

        self.world = world

    def shoot(self):
        self.world.shoot(self)

    def move(self, direction):
        self.x, self.y = self.world.move(self, direction)

    def rotate(self, direction):
        self.angle = self.world.rotate(self, direction)

    def get_vision(self):
        return self.world.get_vision(self)
