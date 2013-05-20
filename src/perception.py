import math
import world
import logging

class Perception:
    """Provides functions to process perception, calculate agent's position etc."""

    location_diff = 0
    location_diff_counter = 0

    def __init__(self):
        pass

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


    def process_vision_perceptors(self, parser_output, w, player_nr):
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
                self.location_diff_counter += 1
                self.location_diff += (localization_result - world.Vector(-14, 9)).mag()
                logging.debug("location_diff: " + str(self.location_diff / self.location_diff_counter))
                w.entity_from_identifier['P' + str(player_nr)]._position = localization_result

        #logging.debug('process_vision_perceptors END')

    def self_localization(self, static_entities, w):
        """Calculates the own agent's position given the perception of some static entities (static_entities)
        and the world (w). (NO LINES YET!)"""

        PERCEPTOR_HEIGHT = 0.5 + 1/30 # calculated w/ simspark - should be really veeeery accurate
        
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
        
        #logging.debug("static entity count: " + str(len(static_entities)))
        
        position_list = []
        see_vector_list = []
        for list1 in static_entities:
            # polar coords as list:
            pol1 = self.get_pol_from_parser_entity(list1)
            
            #distance from 3D Sphere to 2d cartesian
            d_s_o1 =  (pol1[0]**2 - (w.entity_from_identifier[list1[0]]._perception_height - PERCEPTOR_HEIGHT)**2 )**(0.5)
            #define the center
            v1 = world.Vector(w.get_entity_position(list1[0]).x, w.get_entity_position(list1[0]).y)
            a1 = pol1[1]
            for list2 in static_entities:
                if list1[0] != list2[0]:
                    # polar coords as list:
                    pol2 = self.get_pol_from_parser_entity(list2)
                    #distance from 3D Sphere to 2d cartesian
                    d_s_o2 = (pol2[0]**2 - (w.entity_from_identifier[list2[0]]._perception_height - PERCEPTOR_HEIGHT)**2 )**(0.5)
                    #define the center
                    v2 = world.Vector(w.get_entity_position(list2[0]).x, w.get_entity_position(list2[0]).y)
                    a2 = pol2[1]
                    
                    if d_s_o1 > 0 and d_s_o2 > 0 and abs(a1 - a2) > 2*math.pi/180: #die 2 grad sind ausgedacht, mal nachrechnen was wirklich gut waere; NICHT GUT Genug!
                        trig_res = self.trigonometry(v1, d_s_o1, a1, v2, d_s_o2, a2) # , d_s_o1, d_s_o2 # why the fuck was this here?
                        position_list += [trig_res[0]]
                        see_vector_list += [trig_res[1]]
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
        # weighting (still to be done)
        for e in position_list:
            #logging.debug(str(e[0]))
            pass
        '''
        
        # calculate arithmetic mean of all positions and see vectors:
        pos = None
        see = None
        if len(position_list) > 0:
            pos = world.Vector(0, 0)
            for p in position_list:
                pos = pos + p
            pos = pos / len(position_list)
            see = world.Vector(0, 0)
            for s in see_vector_list:
                see = see + s
            see = see / len(see_vector_list)
        #logging.debug('see_vector: ' + str(see))
        
        # now we've got a pretty decent location, but that's not enough!!!!!!!!!!1111111111111
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
        
        return pos


    def get_pol_from_parser_entity(self, entity, which_pol = 0):
        """Returns the polar coordinates in a parser block (entity block)
        as a list like: [distance, angle_hor, angle_vert]
        which_pol is 0 or 1 (default 0) and specifies which pol block
        to use. (Lines can have two.)"""
        return map(float, entity[which_pol + 1][0].split()[1:])


    #def get_nearest_vectors(self, vector, vectors[], how_much):
    #    """Returns the 'how_much' nearest vectors in 'vectors[]' measured to 'vector'."""
    #    temp = sorted(vectors, key=lambda v: (v - vector).mag()) # usin all teh ninja skillz (sort by distance to 'vector')
    #    return temp[:how_much + 1]


    def trigonometry(self, v1, d1, a1, v2, d2, a2):
        """Self localisation by trigonometry.
        Returns a list of 2 vectors: the first representing your position and the second vector the see vector,
        based on the position of the 2 given objects and the distance to them.
        The user has the duty to judge on his own wheater it is a good idea to use a1 ~~ a2 or even a1 = a2.
        Also triangles with sidelength 0 are something you should watch out for yourself.
        This Method will by the way crash when you input v1  = v2, but since static objets dont have the same position..."""
        
        a = (v2-v1).mag()

        b = d2
        c = d1

        #print a,b,c
        acos_arg = (a**2 - b**2 + c**2) / (2.0 * a * c)
        #logging.debug(acos_arg)
        #TODO revise this! (Felix):
        if acos_arg < -1:
            beta = math.pi
        elif acos_arg > 1:
            beta = 0
        else:
            beta = math.acos(acos_arg)
        #print 'beta: ', beta * 180 / math.pi
        v1v2 = v2-v1 #vector from v1 to v2
        v1v2 = v1v2 / v1v2.mag()
        v1v2 = v1v2 * d1

        if a1 > a2: #positive angle means left
            #rotate along the clock (left object)
            beta = -1* beta
        x = v1v2.x * math.cos(beta) - v1v2.y * math.sin(beta)
        y = v1v2.x * math.sin(beta) + v1v2.y * math.cos(beta)
        #print 'v1 to nao ', Vector(x,y), v1
        position = v1 + world.Vector(x, y)
        
        #calculate see vector
        posv1 = v1 - position #vector from our position to v1

        #now rotate with alpha in same direction as when calculating the position
        x = posv1.x * math.cos(a1) - posv1.y * math.sin(a1)
        y = posv1.x * math.sin(a1) + posv1.y * math.cos(a1)

        see_vector = world.Vector(x,y)
        see_vector = see_vector / see_vector.mag()

        return position, see_vector
        
        #return position

