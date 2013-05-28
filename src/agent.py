#!/usr/bin/python
# -*- coding: utf-8 -*-

import sock
import parser
import world
import perception
import logging
import tactics_main
import movement
import nao
import keyframe_engine


class Agent:
    def __init__(self,p_nr):
        self.player_nr = p_nr #TODO needs to be revised for multiple players

        self.world = world.World(6, 30, 20) # 6 players per team, field size: 30 meters x 20 meters
        
        self.nao = nao.Nao(self.world, self.player_nr)

        self.perception = perception.Perception(self.player_nr)

        #setup a socket-connection to the server
        self.socket = sock.Sock("localhost", 3100, "DAI-Labor", self.player_nr)
        self.start()

    def start(self):
        #start listen#self.perception.process_vision_perceptors(parsed_stuff, self.world)ing
        self.socket.start()


        m = movement.Movement(self.world, self.socket, self.player_nr)
        kfe = keyframe_engine.Keyframe_Engine(self.nao, self.socket)
        #t = tactics_main.TacticsMain(self.world, m, self.player_nr)
        
        self.socket.enqueue("beam -5 5 0.5")
        self.socket.flush()
        

        #Beispiel fuer laufen
        #Zielkoordinaten duerfen nicht 0 sein, sonst crash
        #Durch das drehen des sichtfeldes crashed ab und zu die 
        #trigonometry funktion der perception klasse
        #siehe kommentare in der movement klasse fuer workaround 
        #velocity und divergence kann in init angepasst werden (velocity immer < divergence)

        #m.run(-14, 0)
        t = False
        
        while True:
            msg = self.socket.receive()
            #logging.debug(msg)
            parsed_stuff = parser.parse_sexp(msg)
            self.perception.process_vision(parsed_stuff, self.world)
            self.perception.process_gyros(parsed_stuff, self.nao)

            #logging.debug('gyro rate: ' + str(self.nao._gyro_rate))
            #logging.debug('gyro state: ' + str(self.nao.get_gyro_state()))
            
            #lets the nao stand up from back
                        
            #logging.debug('agent location: ' + str(self.world.get_entity_position('P' + str(self.player_nr))))
            #logging.debug('agent location: ' + str(self.nao.get_position()))
            #logging.debug('agent see vector: ' + str(self.nao.get_see_vector()))
            
            if(not t):
              m.run(-15,0)
              t = True
            else:
              m.update()
            self.socket.flush()

            #m.update()
            #t.run_tactics()

            # self.socket.enqueue("(beam "+str(x)+" "+str(y)+" 0)")
            # logging.debug(world.w.flags[0].get_position().x)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    Agent(0)
