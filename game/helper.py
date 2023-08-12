import math
import game.world as w


def check_wall_collisions(circle_center, circle_radius, rect_pos, rect_width, rect_height):
    circle_distance_x = abs(circle_center[0] - rect_pos[0])
    circle_distance_y = abs(circle_center[1] - rect_pos[1])

    if circle_distance_x > (rect_width / 2 + circle_radius):
        return False
    if circle_distance_y > (rect_height / 2 + circle_radius):
        return False

    if circle_distance_x <= (rect_width / 2):
        return True
    if circle_distance_y <= (rect_height / 2):
        return True

    corner_distance_sq = (circle_distance_x - rect_width / 2) ** 2 + (circle_distance_y - rect_height / 2) ** 2
    return corner_distance_sq <= (circle_radius ** 2)


def load_level(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()
    return [line for line in lines]


def check_intersections(start_coordinates, end_coordinates, world, world_object=None, soldier=None):
    for wall in world.walls:
        if world_object == wall:
            continue

        if wall.clipline(start_coordinates, end_coordinates):
            return True

    for s in world.soldiers:
        if s == soldier or s == world_object:
            continue

        if (start_coordinates[0] < s.x < end_coordinates[0] or end_coordinates[0] < s.x < start_coordinates[0]) and \
                (start_coordinates[1] < s.y < end_coordinates[1] or end_coordinates[1] < s.y < start_coordinates[1]):

            dx = (end_coordinates[0] - start_coordinates[0])
            dy = (end_coordinates[1] - start_coordinates[1])
            line_length = math.sqrt(dx ** 2 + dy ** 2)
            circle_distance = abs((dx * (start_coordinates[1] - s.y)) -
                                  (dy * (start_coordinates[0] - s.x))) / line_length

            if circle_distance <= w.CIRCLE_RADIUS:
                return True

    return False
