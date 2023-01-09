import math
import pygame


class K(list):
    default_colour               = (255, 255, 255)    #red, green, blue
    size_proportion              = 0.45
    min_gap                      = 3
    matched_radius_proporition   = 0.5
    unmatched_radius_proporition = 0.285
    circle_radius_proportion     = 0.25

    def __init__(self, *arguments):
        list.__init__(self, *arguments)
        self.colour = K.default_colour

    def set_colour(self, new_colour):
        self.colour = new_colour

    def draw(self, surface, radius=None, coordinates=None):
        if radius is None:
            coordinates, radius = K.get_default_dimensions(coordinates, surface)
        centre_x, centre_y = coordinates
        max_child_radius   = radius - K.min_gap
        self_length        = len(self)
        if self_length > 0:
            corners = K.get_parts(centre_x, centre_y, radius, self_length)
            half    = K.get_parts(centre_x, centre_y, radius / 2, self_length)
            if self_length > 1:
                self.draw_children(half, max_child_radius, radius, self_length, surface)
            else:
                self[0].draw(surface, max_child_radius, (centre_x, centre_y))
            if self_length > 2:
                pygame.draw.polygon(surface, self.colour, corners + [corners[0]], 1)
            else:
                pygame.draw.circle(surface, self.colour, coordinates, radius, 1)
        else:
            pygame.draw.circle(surface, self.colour, coordinates, radius, 1)

    def draw_children(self, half, max_child_radius, radius, self_length, surface):
        for child_index, child in enumerate(self):
            radius_proportion = K.get_radius_proportion(child, self_length)
            child.draw(surface, min(radius_proportion * radius, max_child_radius),
                       half[child_index])

    @staticmethod
    def get_radius_proportion(child, self_length):
        child_length = len(child)
        if child_length > 2:
            if child_length == self_length:
                radius_proportion = K.matched_radius_proporition
            else:
                radius_proportion = K.unmatched_radius_proporition
        else:
            radius_proportion = K.circle_radius_proportion
        return radius_proportion

    @staticmethod
    def get_default_dimensions(coordinates, surface):
        width, height = surface.get_size()
        min_dimension = min(width, height)
        radius = K.size_proportion * min_dimension
        if coordinates is None:
            coordinates = int(width / 2), int(height / 2)
        return coordinates, radius

    @staticmethod
    def get_centre(full, sides, corners, dimension):
        return sum([corn[dimension] * sides[corn_index] for corn_index, corn in
                    enumerate(corners)]) / full

    @staticmethod
    def get_parts(center_x, centre_y, radius, number_of_parts):
        radians_per_corner = 2 * math.pi / number_of_parts
        corners = [(int(center_x + 0.5 + radius * math.cos(corner * radians_per_corner)),
                    int(centre_y + 0.5 + radius * math.sin(corner * radians_per_corner)))
                   for corner in range(0, number_of_parts)]
        return corners

    @staticmethod
    def distance(start, finish):
        x = finish[0] - start[0]
        y = finish[1] - start[1]
        return math.sqrt(x * x + y * y)


if __name__ == '__main__':
    foot, calf, knee, thigh = K(), K(), K(), K()
    leg = K([foot, calf, knee, thigh])
    eye, ear, mouth, nose = K(), K(), K(), K()
    eyes = K([eye, eye])
    ears = K([ear, ear])
    tail, torso, shoulders = K(), K(), K()
    legs = K([leg, leg, leg, leg])
    head = K([ears, eyes, nose, mouth])
    body = K([legs, torso, shoulders])
    dog = K([head, body, tail])

    pygame.init()
    screen = pygame.display.set_mode([800, 800])
    pygame.display.set_caption("Any key to quit")

    dog.draw(screen)

    while True:
        for event in pygame.event.get():
            if event.type in (pygame.QUIT, pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                exit()
        pygame.display.flip()