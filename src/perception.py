import math
import world
import logging

class Perception:
    """Provides functions to process perception, calculate agent's position etc."""
    
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
        
        localisation_result = self.self_localisation(static_entities, w)
        if localisation_result:
            w.entity_from_identifier['P' + str(player_nr)].position = localisation_result

        logging.debug('process_vision_perceptors END')

    def self_localisation(self, static_entities, w):
        """Calculates the own agent's position given a list of static entities. (NO LINES YET!)
        """
        PERCEPTOR_HEIGHT = 0.54
        #PERCEPTOR_HEIGHT = 4.358999999999999  - 0.39/2.0 #(0.39+1.41+0.2+1.3+0.964+0.095) - 0.39/2.0 #nao height - half head's size ,ich glaub das ist veraltet
        #stimmt das wirklich???? ist von hier: http://simspark.sourceforge.net/wiki/index.php/Models
        
        '''     so sieht static_entities aus
        [               
        [L ,['pol',d,phi,theta]]
        ...
        ]'''
        #seperate Lines
        lines = []
        #how do we handle lines? they only have absolute start and endpoints 
        #we can only use them if we are able to identify which line it actually is
        static_entities_wo_lines = [] # without lines
        for l in static_entities:
            if l[0] == 'L':
                lines.append(l)
                static_entities.remove(l)
            else:
                static_entities_wo_lines.append(l)
                
        position_list = []
        #see_vector_list = []
        for list1 in static_entities_wo_lines:
            # polar coords as list:
            pol1 = map(float, list1[1][0].split()[1:]) # looks like [distance, a1, a2]
            #distance from 3D Sphere to 2d cartesian
            logging.debug(str(list1[0]))
            logging.debug(str(list1[1]))
            d_s_o1 =  (pol1[0]**2 - (w.entity_from_identifier[list1[0]]._perception_height - PERCEPTOR_HEIGHT)**2 )**(0.5)
            #define the center
            v1 = world.Vector(w.get_entity_position(list1[0]).x, w.get_entity_position(list1[0]).y)
            a1 = pol1[1]
            for list2 in static_entities_wo_lines:
                if list1[0] != list2[0]:
                    # polar coords as list:
                    pol2 = map(float, list2[1][0].split()[1:]) # looks like [distance, a1, a2]
                    #distance from 3D Sphere to 2d cartesian
                    d_s_o2 = (pol2[0]**2 - (w.entity_from_identifier[list2[0]]._perception_height - PERCEPTOR_HEIGHT)**2 )**(0.5)
                    #define the center
                    v2 = world.Vector(w.get_entity_position(list2[0]).x, w.get_entity_position(list2[0]).y)
                    a2 = pol2[1]

                    if d_s_o1 > 0 and d_s_o2 > 0 and abs(a1 - a2) > 2*math.pi/180: #die 2 grad sind ausgedacht, mal nachrechnen was wirklich gut waere; NICHT GUT Genug!
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
            pos = world.Vector(0,0)       
            for e in position_list:
                pos = pos + e[0]

            return pos / len(position_list)

                
        '''to do:
        + winkel in degree oder radian? -> grad
        + sinnvollen wert fuer die Winkeldifferenz, ab wann triangulation nicht mehr sicher ist, oder irgendwie beide Werte verarbeiten
        (wenn ich sowieso extrem falsche werte raushaue kann man ja beide berechnen lassen)
        + confidency?
        + gewichten
        + Linien benutzen
        + see_vector berechnen
        '''
        '''Ideen:
        + muss das ganze nicht in die agenten klasse, weil man zugriff auf das Selbstmodell und die eigene id braucht?
        + zu stark abweichende werte aussortieren? abweichung von mehr als 2 sigma
        + die eigene position noch mal ueber den Winkel berechnen und dann mit dem anderen Wert vergleichen
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
        position = v1 + world.Vector(x,y)

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

#g = ((15**2+1.05**2) + (0.8 - 0.54)**2)**0.5
#f = (15**2+10**2)**0.5
#logging.debug('vermutete eigene Position: ' + str(w.self_localisation([['G1R' ,['pol',g,-0.6,0.6]],['G2R' ,['pol',g,0.6,0.6]],['F1R' ,['pol',f,-1,0.6]],['F2R' ,['pol',f,1,0.6]]])))
#logging.debug('vermutete eigene Position: ' + str(w.self_localisation([['G1L' ,['pol',g,0.6,0.6]],['G2L' ,['pol',g,-0.6,0.6]],['F1L' ,['pol',f,1,0.6]],['F2L' ,['pol',f,-1,0.6]]])))
