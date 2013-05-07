"""Organizes world data structures and its calculation.
Calculation may be transferred into a separate module in the future."""

import logging
import copy

class Vector:
    """A 2-dimensional vector defined by its cartesian x and y coordinates.
    Used for positions and velocities.
    A third dimension might be added in the future.
    Or a separate Vector3 class or something."""

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def shift(self, dx, dy):
        self.x += dx
        self.y += dy
        return self


class WorldEntity:
    """Basic world entity.
    This can be everything located on the game field and
    the game field itself."""

    def __init__(self, identifier, x, y):
        self._position = Vector(x, y)
        self._identifier = identifier

    def get_position(self):
        return copy.deepcopy(self._position)

    def get_identifier(self):
        return copy.deepcopy(self._identifier)


# STATIC ENTITIES #
class StaticEntity(WorldEntity):
    """Basic static world entity.
    Probably a part of the game field.
    Read-only access to its position."""

    def __init__(self, identifier, x, y):
        WorldEntity.__init__(self, identifier, x, y)

class Line(StaticEntity):
    """A line on the game field defined by two vectors."""

    def __init__(self, identifier, x1, y1, x2, y2):
        self.position2 = Vector(x2, y2)
        StaticEntity.__init__(self, identifier, x1, y1)

class Flag(StaticEntity):
    """A corner flag defined by its position (vector)."""

    def __init__(self, identifier, x, y):
        StaticEntity.__init__(self, identifier, x, y)

class GoalPole(StaticEntity):
    """One of the four goal poles on the game field.
    Defined by its position (vector), height and radius."""

    def __init__(self, identifier, x, y, height, radius):
        self.height = height
        self.radius = radius
        StaticEntity.__init__(self, identifier, x, y)


# MOBILE ENTITIES #
class MobileEntity(WorldEntity):
    """Basic mobile world entity.
    Probably a player or the ball.
    Has random access to its position"""

    def __init__(self, identifier):
        """Constructor doesn't take position, because a mobile entity's
        position is not known at time of initialisation."""
        self.velocity = Vector(0.0, 0.0)
        self.timestamp = 0
        self.confidency = 0.0
        WorldEntity.__init__(self, identifier, 0.0, 0.0)

    def set_position(self, x, y):
        self._position.x = x
        self._position.y = y

class Player(MobileEntity):
    """A player/robot/bot/NAO.
    It has a team, a looking direction (seeVector) and MobileEntity's attributes.
    Will be storing tactical information in the future (currentJob)."""

    def __init__(self, identifier, team):
        self.team = team
        self.seeVector = Vector(0.0, 0.0)
        MobileEntity.__init__(self, identifier)

class Ball(MobileEntity):
    """The ball.
    It has a mass and a radius (plus MobileEntity's attributes)."""

    def __init__(self, radius, mass):   # radius: meter. mass: gram
        self.radius = radius
        self.mass = mass
        MobileEntity.__init__(self, 'B')


class World:
    """The world is a composition of all world entities."""

    entity_from_identifier = [] # will store [indentifier, entity] pairs

    def __init__(self, players_per_team, width, height):
        """Sets up the world as described here:
        http://simspark.sourceforge.net/wiki/index.php/Soccer_Simulation"""

        width_half = width / 2.0
        height_half = height / 2.0

        # set up linez:
        self.lines = [
            Line('L1', -width_half, -height_half, width_half, -height_half),  # top
            Line('L2', -width_half, height_half, width_half, height_half),    # bottom
            Line('LL', -width_half, -height_half, -width_half, height_half),  # left
            Line('LR', width_half, -height_half, width_half, height_half),    # right
            Line('LM', 0.0, -height_half, 0.0, height_half)                   # middle
            # missing: middle circle + lines @ goals
        ]

        # set up flagz:
        self.flags = [
            Flag('F1L', -width_half, -height_half),    # top-left
            Flag('F1R', width_half, -height_half),     # top-right
            Flag('F2L', -width_half, height_half),     # bottom-left
            Flag('F2R', width_half, height_half)       # bottom-right
        ]

        # set up goalz:
        goal_width = 2.1
        self.goal_poles = [
            GoalPole('G1L', -width_half, -goal_width / 2, 0.8, 0.02),   # top/northern left
            GoalPole('G2L', -width_half, goal_width / 2, 0.8, 0.02),    # bottom/south left

            GoalPole('G1R', width_half, -goal_width / 2, 0.8, 0.02),   # top/northern right
            GoalPole('G2R', width_half, goal_width / 2, 0.8, 0.02),    # bottom/south right
        ]

        # set up playerz:
        # add to identifier dictionary:
        self.players = [Player('P', 1)] * players_per_team + [Player('P', 2)] * players_per_team
        # 'P' + id would be a better identifier... but where to get the official player ids?

        # set up ball:
        self.ball = Ball(0.04, 26)


    def create_entity_dict(self):
        """Creates the entity_from_identifier dictionary.
        It only contains all the static entities atm, because of unclear player identifiers."""

        # collect all entities:
        entities = self.lines + self.flags + self.goal_poles
        for entity in entities:
            self.entity_from_identifier += [entity.get_identifier(), entity]

    def get_entity_position(self, identifier):
        """Get an entity's position by its identifier."""

        return self.entity_from_identifier[identifier].get_position()

    def get_parser_part(self, descriptor, parser_output):
        """Get a parser output part specified by its descriptor (e.g. 'See')"""

        # parser_output is like [['See', ['G2R', ['pol', 16.48, -8.05, 0.83]], ...], ...]
        for part in parser_output:
            # part is like ['See', ['G2R', ['pol', 16.48, -8.05, 0.83]], ...]
            if part[0] == descriptor:
                temp = part[1:]
                logging.debug('temp: ' + str(temp))
                # temp is see without 'See'
                # like [['G2R', ['pol', 16.48, -8.05, 0.83]], ...]
                return temp
        # if not found:
        return None

    def process_vision_perceptors(self, parser_output):
        """Processes the parser's output and updates the world info."""

        logging.debug('process_vision_perceptors BEGIN')
        logging.debug('parser_output: ' + str(parser_output))

        # vision only:
        #see = parser_output['See']
        see = self.get_parser_part('See', parser_output)
        # split mobile and static entities:
        static_entity_keys = ['G1L', 'G2L', 'G1R', 'G2R', 'F1L', 'F2L', 'F1R', 'F2R', 'L'] # goals, flags, lines
        static_entities = []
        mobile_entities = []
        logging.debug('see: ' + str(see))

        # give up if no see info available:
        if see:
            # see info is in teh houze. yay.
            for block in see:
                # block is like ['G2R', ['pol', 16.48, -8.05, 0.83]]
                key = block[0]
                value = block[1]
                if key in static_entity_keys:
                    static_entities.append([key, value])
                else:
                    mobile_entities.append([key, value])

            logging.debug('static_entities: ' + str(static_entities))

        # find out our position first:
        # we have static entity positions + vision
        # http://edu.dai-labor.de/wiki/index.php/MPGI3-RC-13S_Datenstrukturen#Eigene_Position_bestimmen
        # feel free to continue yourself :)

        logging.debug('process_vision_perceptors END')


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
w = World(6, 30, 20) # 6 players per team, field size: 30 meters x 20 meters
