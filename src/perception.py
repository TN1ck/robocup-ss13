# -*- coding: utf-8 -*-

import math
import world
import logging
import numpy

class Perception:
    """Provides functions to process perception, calculate agent's position etc."""

    location_diff = 0
    location_diff_counter = 0

    PERCEPTOR_HEIGHT = 0.5 + 1.0 / 30.0 # calculated w/ simspark - should be really veeeery accurate

    def __init__(self, player_nr):
        self.player_nr = player_nr
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


    def process_vision_perceptors(self, parser_output, w):
        """Processes the parser's output and updates the world info."""

        #logging.debug('process_vision_perceptors BEGIN')
        #logging.debug('parser_output: ' + str(parser_output))

        # vision only:
        see = self.get_parser_part('See', parser_output)
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
            localization_result = self.self_localization(static_entities, w)
            if localization_result:
                #logging.debug("localization_result: " + str(localization_result))
                #self.location_diff_counter += 1
                #self.location_diff += (localization_result - world.Vector(-14, 9)).mag()
                #logging.debug("location_diff: " + str(self.location_diff / self.location_diff_counter))
                player = w.entity_from_identifier['P' + str(self.player_nr)]
                player._position = localization_result[0]
                player._see_vector = localization_result[1]
                
                # if self localization was successful, calculate positions of mobile enties:
                self.mobile_entity_localization(mobile_entities, w)
                
        #logging.debug('process_vision_perceptors END')

    def mobile_entity_localization(self, mobile_entities, w):
        """Calculates the position of the given percepted mobile entities and
        writes this info into the given world."""
        for me in mobile_entities: # me = mobile entity
            if me[0] == 'P': # it's a player!
                id = int(me[2][1])
                if id != self.player_nr: # don't process own arms etc.
                    pass
            elif me[0] == 'B': # it's a ball!
                pass
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
            logging.debug("localization failed. static entities: " + str(len(static_entities)))
            return
        
        ## calculate NAO's position ##
        
        position_list = []
        for se1 in static_entities:
            # static entity's polar coords as list:
            pol1 = self.get_pol_from_parser_entity(se1)
            # calculate cartesian 2d distance from 3d distance:
            d_s_o1 = (pol1[0]**2 - (w.entity_from_identifier[se1[0]]._perception_height - self.PERCEPTOR_HEIGHT)**2 )**(0.5)
            # define the center:
            v1 = world.Vector(w.get_entity_position(se1[0]).x, w.get_entity_position(se1[0]).y) #TODO get rid of constructor?
            a1 = pol1[1]
            for se2 in static_entities:
                if se1[0] != se2[0]:
                    # polar coords as list:
                    pol2 = self.get_pol_from_parser_entity(se2)
                    # 2d distance:
                    d_s_o2 = (pol2[0]**2 - (w.entity_from_identifier[se2[0]]._perception_height - self.PERCEPTOR_HEIGHT)**2 )**(0.5)
                    # define the center:
                    v2 = world.Vector(w.get_entity_position(se2[0]).x, w.get_entity_position(se2[0]).y)
                    a2 = pol2[1]
                    
                    if d_s_o1 > 0.1 and d_s_o2 > 0.1 and abs(a1 - a2) > 2.0:
                        trig_res = self.trigonometry(v1, d_s_o1, a1, v2, d_s_o2, a2)
                        if trig_res != None:
                            position_list += [ trig_res ]
        
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
        #logging.debug(' ')

        see_vector_list = []
        for se in static_entities:
            #logging.debug('processing : ' + se[0])
            
            se_pos = w.get_entity_position(se[0])
            se_height = w.entity_from_identifier[se[0]]._perception_height
            #logging.debug('position: ' + str(se_pos) + ' height: ' + str(se_height))
            
            se_pol = self.get_pol_from_parser_entity(se)
            #logging.debug('pol to se: ' + str(se_pol))
            
            # construct a vector from our camera to the static entity:
            see = numpy.array([se_pos.x - pos.x, se_pos.y - pos.y, se_height - self.PERCEPTOR_HEIGHT])
            #logging.debug('vector to se: ' + str(see))
            
            # now some rotationz...
            z_axis = numpy.array([0, 0, 1]) # horizontally
            y_axis = numpy.array([0, 1, 0]) # vertically
            # 2d part of the vector -> angle is:
            rot2d = numpy.arctan2(see[0], see[1]) - math.pi / 2.0 # arctan2 = 0 if vector = [ 0, 1 ]
            #logging.debug('2d rotation: %f' % (rot2d * 180.0 / math.pi) + '°')

            # reset 2d rotation:
            see = numpy.dot(self.rotation_matrix(z_axis, -rot2d), see)
            #logging.debug('after -rot2d: ' + str(see))
            #logging.debug('2d in deg: %f' % ((numpy.arctan2(see[0], see[1]) - math.pi / 2.0) * 180.0 / math.pi) + '°')
            
            # apply (subtract) vertical rotation (-> around y axis):
            see = numpy.dot(self.rotation_matrix(y_axis, -se_pol[2] / 180.0 * math.pi), see) # subtraction is approved
            #see = numpy.dot(self.rotation_matrix(y_axis, -45.0 / 180.0 * math.pi), see)
            #logging.debug('after vert rot: ' + str(see))
            # correct til here
            
            # apply (add) horizontal rotation and re-apply 2d rotation:
            see = numpy.dot(self.rotation_matrix(z_axis, se_pol[1] / 180.0 * math.pi + rot2d), see)
            # addition is approved (in simspark pol right means negative values)
            #see = numpy.dot(self.rotation_matrix(z_axis, -45.0 / 180.0 * math.pi), see)
            #logging.debug('after hor rot: ' + str(see))

            # add to list:
            see_vector_list += [see]
            
            #logging.debug(' ')
        
        see = None
        if len(see_vector_list) > 0:
            see = numpy.array([0, 0, 0])
            for s in see_vector_list:
                see = see + s
            see = see / numpy.linalg.norm(see)
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
        
        return pos, see


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
        Returns a list of 2 vectors: the first representing your position and the second vector the see vector,
        based on the position of the 2 given objects and the distance to them.

        returns None if the parameters don't form a triangle"""
        
        a = (v2-v1).mag()

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
        elif acos_arg > 1:
            beta = 0
        else:
            beta = math.acos(acos_arg) 
        
        v1v2 = v2-v1 #vector from v1 to v2
        v1v2 = v1v2 / v1v2.mag()
        v1v2 = v1v2 * d1


        if a1 > a2: 
            #rotate along the clock (because it is the left object)
            #by the way a positive angle means left of the nao see vector
            beta = -1* beta

        #print 'beta: ', beta * 180 / math.pi

        #print v1v2.rotate(-beta)
        position = v1 + v1v2.rotate(beta)
        
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
