# -*- coding: utf-8 -*-

import math
import world
import drawing
import logging
import collections
import numpy
import copy
from math import log, atan2

def lower_confidence(c):
    return c*0.825

class Perception:
    """Provides functions to process perception, calculate agent's position etc."""

    location_diff = 0
    location_diff_counter = 0
    last_positions = collections.deque([world.Vector(0,0), world.Vector(0,0), world.Vector(0,0), world.Vector(0,0)])  # queue that will keep the last positions of the nao

    PERCEPTOR_HEIGHT = 0.5 + 1.0 / 30.0 # calculated w/ simspark - should be really veeeery accurate

    def __init__(self, player_nr, our_team, drawer):
        self.player_nr = player_nr
        self.our_team = our_team
        self.player_id = 'P_1_' + str(player_nr)
        self.drawer = drawer
        numpy.set_printoptions(precision=3, suppress=True)

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

    def process_joint_positions(self, parser_joint, nao):
        """Takes the parser output and updates the nao with the perceived joint positions."""

        #for part in parser_output:
        #    if part[0] == 'HJ':
        nao.from_perceptor[parser_joint[1][1]].value = parser_joint[2][1]

    def process_gyros(self, parser_gyro, nao):
        """Takes the parser output and updates the nao with the perceived gyro data."""

        # gyro only:
        #gyro = self.get_parser_part('GYR', parser_output)
        gyro = parser_gyro[1:]
        # gyro is like: [['n', 'torso'], ['rt', '0.01', '0.07', '0.46']]

        nao.set_gyro_rate(map(float, gyro[1][1:]))
    def process_accelerometer(self, parser_acc, nao):
        """Takes the parser output and updates the nao with the perceived process_accelerometer data."""

        # example message:(ACC (n torso) (a 0.00 0.00 9.81))
        nao._accelerometer = numpy.array([float(parser_acc[2][1]),float(parser_acc[2][2]),float(parser_acc[2][3])])
        #logging.debug(nao._accelerometer)

    def process_vision(self, parser_see, w):
        """Takes the parser output and updates the world info with the perceived vision data."""

        #logging.debug('process_vision_perceptors BEGIN')
        #logging.debug('parser_output: ' + str(parser_output))

        # vision only:
        #see = self.get_parser_part('See', parser_output)
        see = parser_see[1:]

        # split mobile and static entities:
        static_entity_identifiers = ['G1L', 'G2L', 'G1R', 'G2R', 'F1L', 'F2L', 'F1R', 'F2R', 'L'] # goals, flags, lines
        static_entities = []
        mobile_entities = []
        #logging.debug('see: ' + str(see))

        # give up if no see info available:
        if see:
            # see info is in teh houze. yay.
            for block in see:
                # block is like ['L', ['pol 14.98 -36.73 -2.16'], ['pol 16.03 -39.46 -1.81']]
                identifier = block[0]
                if identifier in static_entity_identifiers:
                    static_entities.append(block)
                else:
                    mobile_entities.append(block)

            #logging.debug('static_entities: ' + str(static_entities))

            # find out our position first:
            player = w.entity_from_identifier[self.player_id]
            player.confidence = lower_confidence(player.confidence)
            localization_result = self.self_localization(static_entities, w)
            if localization_result:
                #logging.debug("localization_result: " + str(localization_result))
                #self.location_diff_counter += 1
                #self.location_diff += (localization_result - world.Vector(-14, 9)).mag()
                #logging.debug("location_diff: " + str(self.location_diff / self.location_diff_counter))
                if localization_result[0] != None and localization_result[1] != None:
                    player._position = localization_result[0]
                    player._see_vector = localization_result[1]
                    player.confidence = 1.0

                # if self localization was successful, calculate positions of mobile enties:
                self.mobile_entity_localization(mobile_entities, w)

        #logging.debug('process_vision_perceptors END')

    def mobile_entity_localization(self, mobile_entities, w):
        """Calculates the position of the given perceived mobile entities and
        writes this info into the given world."""

        # reset confidence in world model:
        for me in w.mobile_entities():
            if me.get_identifier() != self.player_id:
                me.confidence = lower_confidence(me.confidence)

        player = w.entity_from_identifier[self.player_id]
        cam_pos = numpy.array([player.get_position().x, player.get_position().y, self.PERCEPTOR_HEIGHT])
        for me in mobile_entities: # me = mobile entity
            if me[0] == 'P':                            # it's a player!
                # (P (team <teamname>) (id <playerID>) +(<bodypart> (pol <distance> <angle1> <angle2>)))
                # player.team = 1 iff friendly player / player.team = 2 iff hostile player
                team = 1 if me[1][1] == self.our_team else 2
                id = int(me[2][1])
                if id != self.player_nr or team != 1:   # don't process own arms etc.
                    bps = me[3:]                        # bodyparts
                    # collect bodypart positions:
                    pos_list = []
                    for bp in bps:
                        #logging.debug('body part: ' + str(bp))
                        pol = self.get_pol_from_parser_entity(bp)
                        #logging.debug('body part pol: ' + str(pol))
                        vector_to_player = self.add_pol_to_vector(player._see_vector, pol) * pol[0]
                        pos_list += [cam_pos + vector_to_player]
                    # arithmetic mean:
                    pos = numpy.array([0.0, 0.0, 0.0])
                    for pos_item in pos_list:
                        pos += pos_item
                    pos /= len(pos_list)
                    # assemble player identifier:
                    player_key = 'P_' + str(team) + '_' + str(id)
                    # check if player already exists (hostile players don't exist in the beginning):
                    if not player_key in w.entity_from_identifier:
                        # create new player:
                        new_player = world.Player(player_key, team)
                        w.players += [new_player]
                        w.entity_from_identifier[player_key] = new_player
                    w.entity_from_identifier[player_key].set_position(pos[0], pos[1])
                    w.entity_from_identifier[player_key].confidence = 1.0
            elif me[0] == 'B':                          # it's a ball!
                pol = self.get_pol_from_parser_entity(me)
                vector_to_ball = self.add_pol_to_vector(player._see_vector, pol) * pol[0]
                # NAO cam position + vector_to_ball:
                pos = cam_pos + vector_to_ball
                w.entity_from_identifier['B'].set_position(pos[0], pos[1])
                w.entity_from_identifier['B'].confidence = 1.0
            else: # wtf!
                logging.warning('found unknown entity: ' + me[0])

    def self_localization(self, static_entities, w):
        """Calculates the own agent's position given the perception of some static entities (static_entities)
        and the world (w). (NO LINES YET!)
        Returns (position, see_vector)."""

        # first, get rid of lines:
        lines = []
        static_entities2 = []
        for se in static_entities:
            if se[0] == 'L':
                lines.append(se)
            else:
                static_entities2.append(se)

        static_entities = static_entities2 # TODO pls revise. looks kinda stupid.

        # give up, if there're less than 2 static entities:
        if len(static_entities) < 2:
            return # not used atm
            last_pos = self.last_positions[0][0]
            last_see = self.last_positions[0][1]
            # Process lines, aren't used at the moment
            # F1L --L1-- F1R
            # |     |    |
            # LL    LM   LR
            # |     |    |
            # F2L --L2-- F2R
            # The server sends s-expression like: ['L', ['pol', 11.67, -59.74, -2.74], ['pol', 12.31, -55.59, -2.6]]
            # using a set could speed this up
            s_e_names = []
            for se in static_entities:
                s_e_names.append(se[0])
            # function that will return i1, i2 if ...
            # Depending of other static entities and the angle to them, we can determine which lines we are seeing
            # Corners
            if static_entities[0][0][0] == 'F' and len(lines) > 1:
                corners = {'F1L': ['LL', 'L1'], 'F1R': ['L1', 'LR'], 'F2R': ['LR', 'L2'], 'F2L': ['L2', 'LL']}
                left_right = lambda x, ids: ids if x[0][1][2] > x[1][1][2] else [ids[1], ids[0]]
                # Filter out the penalty lines
                lines = filter(lambda x: not(x[1][1] + 0.5 > static_entities[0][1][0] or x[2][1] + 0.5 > static_entities[0][1][0]), lines)
                lines[0][0], lines[1][0] = left_right(lines, corners[static_entities[0][0]])
                # logging.debug("I'm looking at the corner of %s, I found the lines %s %s" % (static_entities[0][0], lines[0][0], lines[1][0]))
            # Sees only one line and no static entities
            elif len(static_entities) == 0 and len(lines) == 1:
                # guess position with last known position, not perfet but close enough
                # in which direction is the nao looiking? north = (0,1,0) south = (0,-1,0), west = (-1,0,0), east = (0,1,0)
                directions = {0: 'L1', 1: 'LR', 2: 'L2', 3: 'LL'}  # L1 = north, LR = east, L2 = south, LL = west
                see_angle = atan2(last_see[1], last_see[0])
                main_direction = lambda a: directions[int((a + math.pi/4)/math.pi/2)]
                lines[0][0] = main_direction(see_angle)
                # logging.debug("I'm looking at the line, I don't see anything else %s") % lines[0][0]
            # two lines, no static entities
            elif len(static_entities) == 0 and len(lines) == 1:
                pass




        ## calculate NAO's position ##

        position_list = []
        position_weight = []
        processed = []
        for se1 in static_entities:
            processed += [se1[0]]
            # static entity's polar coords as list:
            pol1 = self.get_pol_from_parser_entity(se1)
            # calculate cartesian 2d distance from 3d distance:
            d_s_o1 = (pol1[0]**2 - (w.entity_from_identifier[se1[0]]._perception_height - self.PERCEPTOR_HEIGHT)**2 )**(0.5)
            # define the center:
            v1 = w.get_entity_position(se1[0])
            a1 = pol1[1]
            for se2 in static_entities:
                #if se1[0] != se2[0]:
                if not se2[0] in processed:
                    # polar coords as list:
                    pol2 = self.get_pol_from_parser_entity(se2)
                    # 2d distance:
                    d_s_o2 = (pol2[0]**2 - (w.entity_from_identifier[se2[0]]._perception_height - self.PERCEPTOR_HEIGHT)**2 )**(0.5)
                    # define the center:
                    v2 = w.get_entity_position(se2[0])
                    a2 = pol2[1]

                    if d_s_o1 > 0.1 and d_s_o2 > 0.1 and abs(a1 - a2) > 2.0:
                        trig_res = self.trigonometry(v1, d_s_o1, a1, v2, d_s_o2, a2)
                        if trig_res != None:
                            position_list += [ trig_res ]
                            #self.drawer.drawCircle(trig_res, 0.2, 3, [180, 170, 120], "all." + self.player_id + ".debug.ownpospart")
                            #logging.debug(str((trig_res - w.get_entity_position('P_1_' + str(self.player_nr))).mag()))
                            #if (trig_res - w.get_entity_position('P_1_' + str(self.player_nr))).mag() > 1:
                            #    logging.debug(str((v1, d_s_o1, a1, v2, d_s_o2, a2)))
                            #    logging.debug('aus der reihe tanzer')
                    else:
                        logging.debug('trigonometry not called. d_s_o1: ' + str(d_s_o1) + ' d_s_o2: ' + str(d_s_o2) + ' a1: ' + str(a1) + ' a2: ' + str(a2))

        # calculate arithmetic mean of all positions:
        pos = None
        if len(position_list) > 0:
            pos = world.Vector(0, 0)
            for p in position_list:
                pos = pos + p
            pos = pos / len(position_list)
        else:
            return # give up, if position could not be calculated

        # pos is our position now, yay!

        ## calculate NAO's see vector ##

        see_sum = numpy.array([0, 0, 0])
        for se in static_entities:
            se_pos = w.get_entity_position(se[0])
            se_height = w.entity_from_identifier[se[0]]._perception_height

            se_pol = self.get_pol_from_parser_entity(se)

            # construct a vector from our camera to the static entity:
            see = numpy.array([se_pos.x - pos.x, se_pos.y - pos.y, se_height - self.PERCEPTOR_HEIGHT])

            # rotate the vector so it points to the vision center instead of the static entity:
            see = self.add_pol_to_vector(see, -numpy.array(se_pol))

            # sum up:
            see_sum += see

        # normalize summed up see vector:
        see = None
        if numpy.linalg.norm(see_sum) > 0: # check if any data was collected in the first place
            see = see_sum / numpy.linalg.norm(see_sum)
        #logging.debug('see_vector: ' + str(see))

        # we've got a pretty decent location, but that's not enough!!!!!!!!!!1111111111111
        # STEP 2 - process linez
        for l in lines:
            pol1 = self.get_pol_from_parser_entity(l)
            pol2 = self.get_pol_from_parser_entity(l, 1)
            if abs(pol1[1]) > 59 or abs(pol1[2]) > 59 or abs(pol2[1]) > 59 or abs(pol2[2]) > 59:
                # line is (probably) truncated
                pass
            else:
                # seen line is (very very likely) the whole line
                pass
        # enqueue the current position and see vector
        self.last_positions.appendleft([pos, see])
        # delete the last one
        self.last_positions.pop()
        return pos, see

    def add_pol_to_vector(self, vector, pol):
        """Returns the rotated 3d-vector by applying the given polar coordinates as a rotation."""
        # init z/y-axis:
        z_axis = numpy.array([0, 0, 1]) # horizontally
        y_axis = numpy.array([0, 1, 0]) # vertically
        # 2d part of the vector -> angle:
        rot2d = numpy.arctan2(vector[1], vector[0]) - math.pi / 2.0 # arctan2 = 0 if vector = [ 0, 1 ]
        # reset 2d rotation:
        result = numpy.dot(self.rotation_matrix(z_axis, -rot2d), vector)
        # apply (subtract) vertical rotation (-> around y axis):
        result = numpy.dot(self.rotation_matrix(y_axis, pol[2] / 180.0 * math.pi), result) # subtraction is approved
        # apply (add) horizontal rotation and re-apply 2d rotation:
        result = numpy.dot(self.rotation_matrix(z_axis, -pol[1] / 180.0 * math.pi + rot2d), result)

        return result

    def get_pol_from_parser_entity(self, entity, which_pol = 0):
        """Returns the polar coordinates in a parser block (entity block)
        as a list like: [distance, angle_hor, angle_vert]
        which_pol is 0 or 1 (default 0) and specifies which pol block
        to use. (Lines can have two.)"""
        #return map(float, entity[which_pol + 1][0].split()[1:])
        return map(float, entity[which_pol + 1][1:])


    #def get_nearest_vectors(self, vector, vectors[], how_much):
    #    """Returns the 'how_much' nearest vectors in 'vectors[]' measured to 'vector'."""
    #    temp = sorted(vectors, key=lambda v: (v - vector).mag()) # usin all teh ninja skillz (sort by distance to 'vector')
    #    return temp[:how_much + 1]

    def rotation_matrix(self, axis, theta):
        axis = axis / numpy.sqrt(numpy.dot(axis, axis))
        a = numpy.cos(theta / 2)
        b, c, d = -axis * numpy.sin(theta / 2)
        return numpy.array([[a * a + b * b - c * c - d * d, 2 * (b * c - a * d), 2 * (b * d + a * c)],
                            [2 * (b * c + a * d), a * a + c * c - b * b - d * d, 2 * (c * d - a * b)],
                            [2 * (b * d - a * c), 2 * (c * d + a * b), a * a + d * d - b * b - c * c]])

    def trigonometry(self, v1, d1, a1, v2, d2, a2):
        """Self localization by trigonometry.
        Returns a world.Vectors representing the agent's position
        based on the position of the 2 given objects and the distance to them.

        Returns None if the parameters don't form a triangle.

        Parameters:
        v1: absolute, cartesian position of a static entity as a world.Vector
        d1: distance to the static entity as obtained from vision perceptor
        a1: horizontal angle of the static entity in the view field as obtained from vision perceptor
        v2, d2, a2: second static entity
        """

        v1v2 = v2 - v1      #vector from v1 to v2

        a = v1v2.mag()
        b = d2
        c = d1

        if b + c <= a:   #no triangle?
            return None


        acos_arg = (a**2 - b**2 + c**2) / (2.0 * a * c)
        #logging.debug(acos_arg)
        #logging.debug(str(a) + ', ' + str(c) + ', ' + str(b))
        #TODO revise this! (Felix):
        # distance error is e.g.: 28.99 - 29.09
        if acos_arg < -1:
            beta = math.pi
            logging.debug('triangle ain\'t no triangle.')
            logging.debug(str(locals()))
        elif acos_arg > 1:
            beta = 0
            logging.debug('triangle ain\'t no triangle.')
            logging.debug(str(locals()))
        else:
            #beta = math.acos(acos_arg)
            beta = numpy.arccos(acos_arg)

        v1v2 = v1v2 / v1v2.mag()
        v1v2 = v1v2 * d1


        if a1 > a2:
            #rotate along the clock (because a1 is the left object)
            #by the way a positive angle means left of the nao see vector
            beta = -1* beta

        #print 'beta: ', beta * 180 / math.pi

        #print v1v2.rotate(-beta)
        position = v1 + v1v2.rotate(beta)
        self.drawer.drawLine(v1, position, 1, [180, 170, 120], "all." + self.player_id + ".debug.ownpospart.line")

        # abs(a1 - a2)
        # a
        # b

        '''
        #calculate see vector
        #with v1
        posv1 = v1 - position #vector from our position to v1
        posv1 = posv1 / posv1.mag()

        #now rotate back with alpha
        alpha = a1*math.pi /180
        alpha *= -1 #reverse the angle
        see_vector = posv1.rotate(alpha)
        #print world.Vector(x,y)

        #with v2
        posv2 = v2 - position #vector from our position to v1
        posv2 = posv2 / posv2.mag()

        #now rotate back with alpha
        alpha = a2*math.pi /180
        alpha *= -1 #reverse the angle

        #print world.Vector(x,y)
        see_vector += posv2.rotate(alpha)

        see_vector = see_vector / see_vector.mag()
        '''

        return position #, see_vector


'''#little testbase
#if you aren't me, dont use it
#(because there is this issue that v1 and v2 has to be chosen in a way,
#so that the triangle is located in the upper right half of the coordinatsystem)
(the trigonometry can handle that, but not the testbase yet XD)
p = Perception()
v1 = world.Vector(1, 1)   #use v1, v2 to define a triangle
v2 = world.Vector(1,-1)
d1 = (v1.x**2 + v1.y**2)**0.5
d2 = (v2.x**2 + v2.y**2)**0.5
a1 = math.atan((1.*v1.y)/v1.x)*180/math.pi
a2 = math.atan((1.*v2.y)/v2.x)*180/math.pi
o = world.Vector(1,2)   #offset to move the triangle
turn = 99              #turn in degree along the clock
t = -1*turn *math.pi/180
see = world.Vector(1,0)
see = world.Vector(see.x * math.cos(t) - see.y * math.sin(t),
        see.x * math.sin(t) + see.y * math.cos(t))

print v1, d1, a1, v2, d2, a2, o
print 'Ergebnis: ' + str(p.trigonometry(v1+o, d1, a1+turn, v2+o, d2, a2+turn))
print 'expected was: ', o, see
'''
