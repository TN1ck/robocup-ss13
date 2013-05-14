# -*- coding: cp1252 -*-
"""Organizes world data structures and its calculation.
Calculation may be transferred into a separate module in the future."""

import logging
import copy

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
        return self.x == other.x and self.y == other.y

    def __str__(self):
        return '(' + str(self.x) + ',' + str(self.y) + ')'

    #magnitude (zu deutsch Betrag)
    def mag(self):
        return (self.x**2 + self.y**2)**0.5


class WorldEntity:
    """Basic world entity.
    This can be everything located on the game field and
    the game field itself."""

    def __init__(self, identifier, x, y):
        self._position = Vector(x, y)
        self._identifier = identifier
        self._perception_heights = 0 # soll jan dann richten ;P (used to compute the distance)

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
        self.confidency = 0.0


    def set_position(self, x, y):
        self._position.x = x
        self._position.y = y

class Player(MobileEntity):
    """A player/robot/bot/NAO.
    It has a team, a looking direction (seeVector) and MobileEntity's attributes.
    Will be storing tactical information in the future (currentJob)."""

    def __init__(self, identifier, team):
        MobileEntity.__init__(self, identifier)
        self.team = team
        self.seeVector = Vector(0.0, 0.0)

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

        # set up playerz:
        self.players = []
        for i in range(players_per_team * 2):
            if i < players_per_team:
                team = 1
            else:
                team = 2
            self.players += [Player('P' + str(i), team)]
        #self.players = [Player('P', 1)] * players_per_team + [Player('P', 2)] * players_per_team

        # set up ball:
        self.ball = Ball(0.04, 26)

        # add everything to identifier dictionary:
        self.create_entity_dict()

    def create_entity_dict(self):
        """Creates the entity_from_identifier dictionary."""

        # collect all entities:
        entities = self.lines + self.flags + self.goal_poles + self.players + [self.ball]
        for entity in entities:
            self.entity_from_identifier[entity.get_identifier()] = entity

    def get_entity_position(self, identifier):
        """Get an entity's position by its identifier."""

        return self.entity_from_identifier[identifier].get_position()


