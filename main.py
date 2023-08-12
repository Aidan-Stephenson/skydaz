from game.world import World
import random
import time

x = World()

for i in range(10000):
    for s in x.soldiers:
        if s.death:
            continue
        s.move(random.choice(["up", "down", "left", "right", ""]))
        if random.choice([0, 1]) == 1:
            s.shoot()
        s.rotate(random.choice(["clockwise", "counter_clockwise", ""]))
    x.next_tick()
    time.sleep(0.01)
