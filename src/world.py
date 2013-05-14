# -*- coding: cp1252 -*-
"""Organizes world data structures and its calculation.
Calculation may be transferred into a separate module in the future."""

import logging
import copy
import math

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


# TODO
class ownPlayer(Player):
    """This class represents our own robot and thus is a singleton class"""
    pass

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
        self.players = [Player('P', 1)] * players_per_team + [Player('P', 2)] * players_per_team
        # 'P' + id would be a better identifier... but where to get the official player ids?

        # set up ball:
        self.ball = Ball(0.04, 26)

        # add to identifier dictionary:
        self.create_entity_dict()

    # TODO
    def get_own_player(self):
        pass

    def create_entity_dict(self):
        """Creates the entity_from_identifier dictionary.
        It only contains all the static entities atm, because of unclear player identifiers."""

        # collect all entities:
        entities = self.lines + self.flags + self.goal_poles
        for entity in entities:
            self.entity_from_identifier[entity.get_identifier()] = entity

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

    def self_localisation(self, static_entities):
        PERCEPTOR_HEIGHT = 0.54
        #PERCEPTOR_HEIGHT = 4.358999999999999  - 0.39/2.0 #(0.39+1.41+0.2+1.3+0.964+0.095) - 0.39/2.0 #nao height - half head's size ,ich glaub das ist veraltet
        #stimmt das wirklich???? ist von hier: http://simspark.sourceforge.net/wiki/index.php/Models
        
        '''	so sieht static_entities aus
        [		
	[L ,['pol',d,phi,theta]]
	...
	]'''
	#seperate Lines
        lines = []
	#how do we handle lines? they only have absolute start and endpoints 
	#we can only use them if we are able to identify which line it actually is
        for l in static_entities:
            if l[0] == 'L':
                lines.append(l)
                static_entities.remove(l)
                
        position_list = []
        #see_vector_list = []
        for list1 in static_entities:		
            #distance from 3D Sphere to 2d cartesian
            d_s_o1 =  (list1[1][1]**2 - (self.entity_from_identifier[list1[0]]._perception_height - PERCEPTOR_HEIGHT)**2 )**(0.5)
            #define the center
            v1 = Vector(self.get_entity_position(list1[0]).x, self.get_entity_position(list1[0]).y)
            a1 = list1[1][2]
            for list2 in static_entities:
                if list1[0] != list2[0]:
                    #distance from 3D Sphere to 2d cartesian
                    d_s_o2 = (list2[1][1]**2 - (self.entity_from_identifier[list2[0]]._perception_height - PERCEPTOR_HEIGHT)**2 )**(0.5)
                    #define the center
                    v2 = Vector(self.get_entity_position(list2[0]).x, self.get_entity_position(list2[0]).y)					
                    a2 = list2[1][2]

                    if d_s_o1 > 0 and d_s_o2 > 0 and abs(a1 - a2) > 2*math.pi/180: #die 2 grad sind ausgedacht, mal nachrechnen was wirklich gut wäre; NICHT GUT Genug!
                        position_list.append([self.trigonometry(v1, d_s_o1, a1, v2, d_s_o2, a2), d_s_o1, d_s_o2])
                    
                    #see_vector_list += [] 
                    
  
        '''
        #error estimilation
        sigma = (0.0965**0.5 ) *2
        average_pos = position_list[0][0]   #what if the first one is already unexceptable far off? better use the pos from the closest object pair
        average_distance = average_pos.mag()
        reduced_sigma = sigma

	for e in position_list:
            for f in position_list:
                # check weather they could intersect (too far away or one is within the other)
                # take the 2 points to define the new average_pos (radius = (p1-p2).mag()/2.0 is the new reduced_sigma)
                l = intersections_circle(e[0], sigma *(e[1]+e[2]/2.0)/100, max_error, reduced_sigma)
                
                if len(l) == 1:
                    if l[0].mag() < average_distance 
        '''
        # weighting (still to be done)
        for e in position_list:
            logging.debug(str(e[0]))
        #logging.debug(str( position_list))
        if len(position_list) != 0:
            pos = Vector(0,0)       
            for e in position_list:
                pos = pos + e[0]

            return pos / len(position_list)

		
        '''to do:
        + winkel in degree oder radian? -> grad
        + sinnvollen wert für die Winkeldifferenz, ab wann triangulation nicht mehr sicher ist, oder irgendwie beide Werte verarbeiten
        (wenn ich sowieso extrem falsche werte raushaue kann man ja beide berechnen lassen)
        + confidency?
        + gewichten
        + Linien benutzen
        + see_vector berechnen
        '''
        '''Ideen:
        + muss das ganze nicht in die agenten klasse, weil man zugriff auf das Selbstmodell und die eigene id braucht?
        + zu stark abweichende werte aussortieren? abweichung von mehr als 2 sigma
        + die eigene position noch mal über den Winkel berechnen und dann mit dem anderen Wert vergleichen
        '''

        
    ''' This method gets 2 vectors and 2 radius
    and returns a list of Vectors representing the intersection points of the circles'''
    def intersections_circle(self, v1, r1, v2, r2):
        ''' our circles
        (x-x1)^2+(y-y1)^2 = r1^2
        (x-x2)^2+(y-y2)^2 = r2^2
        '''
        #calculate chordale
        x = -2.0 * (v1.x - v2.x)
        y = -2.0 * (v1.y - v2.y)
        c = 1.0*r1**2 - r2**2 - v1.x**2 + v2.x**2 - v1.y**2 + v2.y**2
        d = (v2-v1).mag()
        #print x,y,c,d

        #no or just one interesection shouldn't happen in our simulation, because that would require 180 degree view or higher, but just for completeness
        if r1 + r2  < d:    
            return []   #circles to far away from each other
        elif r1+r2 == d:
            return [v1 + (v2-v1)/2.0]
   
        if y != 0:
	    #solve y
            m = -1*x / y 
            c = c / y 
            # -> chordale: y = m*x + c
            #print 'chordale: ' , m, 'x + ', c		
	    #calculate intersection with the circles
	    #P-Q-Formel
            #(x - v1.x)**2 + (m*x + c - v1.y)**2 - r1**2 = x**2 - 2 v1.x * x + v1.x**2   + (m*x+c)**2 - 2*((m*x+c)*v1.y) + (v1.y)**2 - r1**2
            # = 1 *x**2 + m**2 *x**2        + 2*m*x*c  - 2*((m*x+c)*v1.y) - 2*v1.x * x      + v1.x**2  + (v1.y)**2 - r1**2 + c**2
            # =  (m**2+1) *x**2      + 2*m*c *x - 2*m*v1.y *x - 2 v1.x * x      + v1.x**2  + (v1.y)**2 - r1**2 + c**2 -2*c*v1.y
            f = m**2+1
            p = (2*m*c - 2*m*v1.y - 2*v1.x) / f
            q = (v1.x**2  + (v1.y)**2 - r1**2 + c**2 -2*c*v1.y )/ f
            d = p**2/4.0-q
            if d < 0:
                return []
            #print p,q
            x_1 = -(p)/2.0 + (d)**0.5
            y_1 = x_1*m + c 
                                            
            x_2 = -(p)/2.0 - (d)**0.5
            y_2 = x_2*m + c 
        else:
            #print 'y = 0'
            if x == 0:
                return []
                #print 'circles identical, this should never happen' #objects on the same position, we cant use them

            c = c / x
            #we got m*x = c to use in our circle
            #P-Q-Formel
            #(c - v1.x)**2 + (y - v1.y)**2 - r1**2 = y**2 - 2*v1.y *y + (c - v1.x)**2 + v1.y**2 - r1**2
            p = - 2*v1.y
            q = (c - v1.x)**2 + v1.y**2 - r1**2
            d = (p)**2/4.0-q
            if d < 0:
                return []
            y_1 = -(p)/2.0 + (d)**0.5
            x_1 = c
                                            
            y_2 = -(p)/2.0 - (d)**0.5
            x_2 = c 

        p1 = Vector(x_1,y_1)
        p2 = Vector(x_2,y_2)
        if p1 == p2:
            return [p1]
        else:
            return [p1, p2]

        
    ''' self localisation by trigonometry
        returns a list of 2 vectors: the first representing your position and the second vector the see vector,
        based on the position of the 2 given objects and the distance to them.
        the user has the duty to judge on his own wheater it is a good idea to use a1 ~~ a2 or even a1 = a2
        also triangles with sidelength 0 are something you should watch out for yourself 

        This Method will by the way crash when you input v1  = v2, but since static objets dont have the same position ...'''
    def trigonometry(self, v1, d1, a1, v2, d2, a2):
        a = (v2-v1).mag()
        
        b = d2
        c = d1

        #print a,b,c
        beta = math.acos((a**2 - b**2 + c**2) /(2.0*a*c))
        #print 'beta: ', beta * 180 / math.pi
        v1v2 = v2-v1 #vector from v1 to v2
        v1v2 = v1v2 / v1v2.mag()
        v1v2 = v1v2 * d1

        if a1 > a2: #positiv angle means left
            #rotate along the clock (left object)
            beta = -1* beta
        x = v1v2.x * math.cos(beta) - v1v2.y * math.sin(beta)
        y = v1v2.x * math.sin(beta) + v1v2.y * math.cos(beta)
        #print 'v1 to nao ', Vector(x,y), v1
        position = v1 + Vector(x,y)

        ''' bekommen wir unsere Winkel in degree or radian? -> in grad
        #calculate see vector
        posv1 = v1 - pos #vector from our position to v1

        #now rotate with alpha in same direction as when calculating the position
        x = posv1.x * math.cos(a1) - posv1.y * math.sin(a1)
        y = posv1.x * math.sin(a1) + posv1.y * math.cos(a1)

        see_vector = Vector(x,y)
        see_vector = see_vector / see_vector.mag()

        return [ position, see_vector ]
        '''
        return position

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
w = World(6, 30, 20) # 6 players per team, field size: 30 meters x 20 meters

g = ((15**2+1.05**2) + (0.8 - 0.54)**2)**0.5
f = (15**2+10**2)**0.5
logging.debug('vermutete eigene Position: ' + str(w.self_localisation([['G1R' ,['pol',g,-0.6,0.6]],['G2R' ,['pol',g,0.6,0.6]],['F1R' ,['pol',f,-1,0.6]],['F2R' ,['pol',f,1,0.6]]])))
logging.debug('vermutete eigene Position: ' + str(w.self_localisation([['G1L' ,['pol',g,0.6,0.6]],['G2L' ,['pol',g,-0.6,0.6]],['F1L' ,['pol',f,1,0.6]],['F2L' ,['pol',f,-1,0.6]]])))


