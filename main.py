import math, pygame


class K(list):
    default_colour               = (255, 255, 255)    #red, green, blue
    default_min_energy           = 0.00001
    background_colour            = (0, 0, 0)
    force_proportion             = 10000.0
    gather_proportion            = 10.0
    gather_base                  = 0.1
    size_proportion              = 0.4
    min_gap                      = 3
    max_gather_force             = 1.0
    max_repulsion_force          = 1.0
    matched_radius_proporition   = 0.5
    unmatched_radius_proporition = 0.285
    circle_radius_proportion     = 0.25
    tree                         = []
    root                         = None

    def __init__(self, *arguments):
        list.__init__(self, *arguments)
        self.colour   = K.default_colour
        self.velocity = [0.0, 0.0]
        self.position = None
        self.radius   = None
        self.weight   = 1
        K.root        = self
        K.tree.append(self)

    def step(self):
        self.gather()
        for outer in K.tree:
            for inner in K.tree:
                if (outer is not inner) and not (outer in inner):
                    repulsion      = outer.repel(inner)
                    inner.velocity = [inner.velocity[0] + repulsion[0],
                                      inner.velocity[1] + repulsion[1]]
        result = sum([sum([element * element for element in kirillope.velocity])
                      for kirillope in K.tree])
        for outer in K.tree:
            outer.position = [outer.position[0] + outer.velocity[0],
                              outer.position[1] + outer.velocity[1]]
            outer.velocity = [0.0, 0.0]
        return result

    def repel(self, other):
        return K.scale(other.position[0] - self.position[0],
                       other.position[1] - self.position[1],
                       (min(K.max_repulsion_force, other.weight *
                            other.__class__.force_proportion / K.distance_square(
                           other.position, self.position)) / self.weight))

    def gather(self):
        for child in self:
            distance_to_edge = self.radius - K.distance(child.position, self.position)
            if distance_to_edge <= 0:
                amount = K.max_gather_force
            else:
                amount = min(K.gather_base + 1.0 / distance_to_edge, K.max_gather_force)
            acceleration = K.scale(self.position[0] - child.position[0],
                                   self.position[1] - child.position[1],
                                   amount * K.gather_proportion / child.weight)
            child.velocity = [child.velocity[0] + acceleration[0],
                              child.velocity[1] + acceleration[1]]
            child.gather()

    def set_colour(self, new_colour):
        self.colour = new_colour

    def set_weight(self, new_weight):
        self.weight = new_weight

    def spread(self, surface, radius=None, coordinates=None):
        if radius is None:
            coordinates, radius = K.get_default_dimensions(coordinates, surface)
        centre_x, centre_y = coordinates
        max_child_radius   = radius - K.min_gap
        self_length        = len(self)
        if self_length > 1:
            self.spread_children(self.get_parts(centre_x, centre_y, radius, self_length),
                                 max_child_radius, radius, self_length, surface)
        elif self_length > 0:
            self[0].spread(surface, max_child_radius, (centre_x, centre_y))
        self.position = coordinates
        self.radius = radius

    def draw(self, surface):
        [child.draw(surface) for child in self]
        try:
            pygame.draw.circle(surface, self.colour,
                               [int(element + 0.5) for element in self.position],
                                                           self.radius, 1)
        except TypeError:
            print(self.position, self.radius)
            exit()

    def spread_children(self, half, max_child_radius, radius, self_length, surface):
        for child_index, child in enumerate(self):
            radius_proportion = K.get_radius_proportion(child, self_length)
            child.spread(surface, min(radius_proportion * radius, max_child_radius),
                         half[child_index])

    def get_parts(self, centre_x, centre_y, parent_radius, number_of_parts):
        radians_per_corner = 2 * math.pi / number_of_parts
        radius             = parent_radius / 2
        return [(int(centre_x + 0.5 + radius * math.cos(corner * radians_per_corner)),
                 int(centre_y + 0.5 + radius * math.sin(corner * radians_per_corner)))
                for corner in range(0, number_of_parts)]

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
    def distance_square(start, finish):
        x = finish[0] - start[0]
        y = finish[1] - start[1]
        return x * x + y * y

    @staticmethod
    def distance(start, finish):
        return math.sqrt(K.distance_square(start, finish), )

    @staticmethod
    def comparison(x, y):
        if x > y:
            return 1
        if x < y:
            return -1
        return 0

    @staticmethod
    def arrange(surface=None, min_energy=default_min_energy):
        K.root.spread(surface)
        energy = K.root.step()
        while energy > min_energy:
            energy = K.root.step()
            if surface:
                surface.fill(K.background_colour)
                K.root.draw(surface)
                pygame.display.flip()
                for event in pygame.event.get():
                    if event.type in (pygame.QUIT, pygame.KEYDOWN,
                                      pygame.MOUSEBUTTONDOWN):
                        exit()

    @staticmethod
    def scale(x, y, length=1.0):
        if y != 0.0:
            c                = abs(x / y)
            lengthSquare     = length * length
            cSquare          = c * c
            newX             = (K.comparison(length, 0.0) * K.comparison(x, 0.0) *
                                math.sqrt((lengthSquare * cSquare) / (cSquare + 1.0)))
            newXSquare       = newX * newX
            squareDifference = lengthSquare - newXSquare
            if squareDifference > 0.0:
                newY = (K.comparison(length, 0.0) * K.comparison(y, 0.0) *
                        math.sqrt(squareDifference))
                return newX, newY
            return newX, 0.0
        if x != 0.0:
            return K.comparison(x, 0.0) * length, 0.0
        return 0.0, 0.0


if __name__ == '__main__':
    front_left_foot, front_left_calf, front_left_knee, front_left_thigh = K(), K(), K(), K()
    front_right_foot, front_right_calf, front_right_knee, front_right_thigh = K(), K(), K(), K()
    hind_left_foot, hind_left_calf, hind_left_knee, hind_left_thigh = K(), K(), K(), K()
    hind_right_foot, hind_right_calf, hind_right_knee, hind_right_thigh = K(), K(), K(), K()
    front_left_leg = K([front_left_foot, front_left_calf, front_left_knee, front_left_thigh])
    front_right_leg = K([front_right_foot, front_right_calf, front_right_knee, front_right_thigh])
    hind_left_leg = K([hind_left_foot, hind_left_calf, hind_left_knee, hind_left_thigh])
    hind_right_leg = K([hind_right_foot, hind_right_calf, hind_right_knee, hind_right_thigh])
    left_eye, right_eye, left_ear, right_ear, mouth, nose = K(), K(), K(), K(), K(), K()
    tail, torso, shoulders = K(), K(), K()
    head = K([left_ear, right_ear, left_eye, right_eye, nose, mouth])
    dog = K([head, front_left_leg, front_right_leg, hind_left_leg, hind_right_leg, torso, shoulders, tail])

    pygame.init()
    screen = pygame.display.set_mode([900, 600])
    pygame.display.set_caption("Any key to quit")

    K.arrange(screen)

    pygame.image.save(screen, "dog.png")

