# -*- coding: utf-8 -*-
"""Organizes world data structures and its calculation.
Calculation may be transferred into a separate module in the future."""

import logging
import copy
import math
import numpy

class Vector:
    """A 2-dimensional vector defined by its cartesian x and y coordinates.
Used for positions and velocities.
A third dimension might be added in the future.
Or a separate Vector3 class or something.

Notice that Vector(1,2)* 2 is defined but not 2 * Vector (is there a way to do this in Python?)
"""

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def shift(self, dx, dy):
        self.x += dx
        self.y += dy
        return self

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y )

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y )

    def __mul__(self, other):
        return Vector(self.x * other, self.y *other )

    def __div__(self, other):
        return Vector(self.x / other, self.y / other )

    def __eq__(self, other):
        if other == None:
            return False
        else:
            return self.x == other.x and self.y == other.y

    def __repr__(self):
        return 'Vector(' + str(self.x) + ', ' + str(self.y) + ')'

    #angle in radian
    def rotate(self, a):
        x = self.x * numpy.cos(a) - self.y * numpy.sin(a)
        self.y = self.x * numpy.sin(a) + self.y * numpy.cos(a)
        self.x = x

        return self

    #magnitude (zu deutsch Betrag)
    def mag(self):
        #return numpy.linalg.norm(numpy.array([self.x, self.y]))    # time: 2.81
        #return numpy.hypot(self.x, self.y)                         # time: 0.29
        return (self.x**2 + self.y**2)**0.5                         # time: 0.07
        # numpy, y u no better than native python??

    def to_list(self):
        return [self.x, self.y]


class WorldEntity:
    """Basic world entity.
    This can be everything located on the game field and
    the game field itself."""

    def __init__(self, identifier, x, y):
        self._position = Vector(x, y)
        self._identifier = identifier

        """The height an entity is percepted at. (e.g. goal pole is
        percepted at the gole's height, but a flag is percepted at 0."""
        self._perception_height = 0

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
        StaticEntity.__init__(self, identifier, x1, y1)
        self.position2 = Vector(x2, y2)

    def __repr__(self):
        return 'Line(' + str(self._identifier) + ', ' + str(self._position) + ', ' + str(self.position2) + ')'

class Flag(StaticEntity):
    """A corner flag defined by its position (vector)."""

    def __init__(self, identifier, x, y):
        StaticEntity.__init__(self, identifier, x, y)
        self._perception_height = 0

class GoalPole(StaticEntity):
    """One of the four goal poles on the game field.
    Defined by its position (vector), height and radius."""

    def __init__(self, identifier, x, y, height, radius):
        StaticEntity.__init__(self, identifier, x, y)
        self.height = height
        self.radius = radius
        self._perception_height = height


# MOBILE ENTITIES #
class MobileEntity(WorldEntity):
    """Basic mobile world entity.
    Probably a player or the ball.
    Has random access to its position"""

    def __init__(self, identifier):
        """Constructor doesn't take position, because a mobile entity's
        position is not known at time of initialisation."""
        WorldEntity.__init__(self, identifier, 0.0, 0.0)
        self.velocity = Vector(0.0, 0.0)
        self.timestamp = 0
        self.confidence = 0.0

    def set_position(self, x, y):
        self._position.x = x
        self._position.y = y

class Player(MobileEntity):
    """A player/robot/bot/NAO.
    It has a team, a looking direction (see_vector) and MobileEntity's attributes.
    Will be storing tactical information in the future (currentJob)."""

    def __init__(self, identifier, team):
        MobileEntity.__init__(self, identifier)
        self.team = team
        self._see_vector = numpy.array([0.0, 0.0, 0.0])

    def get_see_vector(self):
        return copy.deepcopy(self._see_vector)

class Ball(MobileEntity):
    """The ball.
    It has a mass and a radius (plus MobileEntity's attributes)."""

    def __init__(self, radius, mass):   # radius: meter. mass: gram
        MobileEntity.__init__(self, 'B')
        self.radius = radius
        self.mass = mass

class World:
    """The world is a composition of all world entities."""

    entity_from_identifier = {} # will store [indentifier, entity] pairs

    def __init__(self, players_per_team, width, height):
        """Sets up the world as described here:
        http://simspark.sourceforge.net/wiki/index.php/Soccer_Simulation"""

        width_half = width / 2.0
        height_half = height / 2.0
        penalty = Vector(1.8, 3.9) # penalty area around goals used for line setup

        # set up linez:
        self.lines = [
            Line('L1', -width_half, height_half, width_half, height_half),      # top
            Line('L2', -width_half, -height_half, width_half, -height_half),    # bottom
            Line('LL', -width_half, height_half, -width_half, -height_half),    # left
            Line('LR', width_half, height_half, width_half, -height_half),      # right
            Line('LM', 0.0, height_half, 0.0, -height_half),                    # middle
            # penalty line upper left:
            Line('LG1L', -width_half, penalty.y / 2, -width_half + penalty.x, penalty.y / 2),
            # penalty line lower left:
            Line('LG2L', -width_half, -penalty.y / 2, -width_half + penalty.x, -penalty.y / 2),
            # penalty line frontal left (going north->south):
            Line('LGL', -width_half + penalty.x, penalty.y / 2, -width_half + penalty.x, -penalty.y / 2),
            # penalty line upper right:
            Line('LG1R', width_half, penalty.y / 2, width_half - penalty.x, penalty.y / 2),
            # penalty line lower right:
            Line('LG2R', width_half, -penalty.y / 2, width_half - penalty.x, -penalty.y / 2),
            # penalty line frontal right (going north->south):
            Line('LGR', width_half - penalty.x, penalty.y / 2, width_half - penalty.x, -penalty.y / 2)

            # TODO: find out how the ten circle lines are positioned
        ]
        # center circle lines:
        MIDDLE_CIRCLE_RADIUS = 1.8
        px1 = MIDDLE_CIRCLE_RADIUS
        py1 = 0.0
        count = 0
        for deg in xrange(36, 360 + 36, 36):
            count += 1
            px2 = math.cos(deg * math.pi / 180.0) * MIDDLE_CIRCLE_RADIUS;
            py2 = math.sin(deg * math.pi / 180.0) * MIDDLE_CIRCLE_RADIUS;

            self.lines += [Line('LC' + str(count), px1, py1, px2, py2)]
            #fieldLines.put("MC_" + (deg - 36) + "-" + deg, new Vector2d[] { new Vector2d(px1, py1), new Vector2d(px2, py2) });

            px1 = px2
            py1 = py2
        #logging.debug(str(self.lines))

        # set up flagz:
        self.flags = [
            Flag('F1L', -width_half, height_half),  # top-left
            Flag('F1R', width_half, height_half),   # top-right
            Flag('F2L', -width_half, -height_half), # bottom-left
            Flag('F2R', width_half, -height_half)   # bottom-right
        ]

        # set up goalz:
        goal_width = 2.1
        self.goal_poles = [
            GoalPole('G1L', -width_half, goal_width / 2, 0.8, 0.02),    # top/northern left
            GoalPole('G2L', -width_half, -goal_width / 2, 0.8, 0.02),   # bottom/south left

            GoalPole('G1R', width_half, goal_width / 2, 0.8, 0.02),     # top/northern right
            GoalPole('G2R', width_half, -goal_width / 2, 0.8, 0.02),    # bottom/south right
        ]

        # set up our playerz:
        self.players = []
        for i in range(players_per_team):
            self.players += [Player('P_1_' + str(i+1), 1)]                # 1 ~> our team
        # hostile players are created 'on sight' in perception.py

        # set up ball:
        self.ball = Ball(0.04, 26)

        # universal mobile entity list:
        # self.mobile_entities = self.players + [self.ball]
        # player list is dynamic and this list does not update. use mobile_entities() instead.

        # add everything to identifier dictionary:
        self.create_entity_dict()

    def mobile_entities(self):
        return self.players + [self.ball]

    def create_entity_dict(self):
        """Creates the entity_from_identifier dictionary."""

        # collect all entities:
        entities = self.lines + self.flags + self.goal_poles + self.players + [self.ball]
        for entity in entities:
            self.entity_from_identifier[entity.get_identifier()] = entity

    def get_entity_position(self, identifier):
        """Get an entity's position by its identifier."""
        return self.entity_from_identifier[identifier].get_position()
