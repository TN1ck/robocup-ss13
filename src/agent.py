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
from sys import argv

global our_team
our_team = "DAI-Labor"



class Agent:
    def __init__(self,p_nr):
        self.player_nr = p_nr #TODO needs to be revised for multiple players

        self.world = world.World(6, 30, 20) # 6 players per team, field size: 30 meters x 20 meters

        self.nao = nao.Nao(self.world, self.player_nr)

        self.perception = perception.Perception(self.player_nr)

        #setup a agentSocket-connection to the server
        self.agentSocket = sock.Sock("localhost", 3100, our_team, self.player_nr)
        self.monitorSocket = sock.Sock("localhost", 3200, None, None)
        self.start()

    def start(self):
        #start listen#self.perception.process_vision_perceptors(parsed_stuff, self.world)ing
        self.agentSocket.start()
        self.monitorSocket.start()

       


        m = movement.Movement(self.world, self.agentSocket, self.player_nr)
        kfe = keyframe_engine.Keyframe_Engine(self.nao, self.agentSocket)
        t = tactics_main.TacticsMain(self.world, m, self.nao)

        # You need a first flush in order that "beam" works
        self.agentSocket.flush()

        msg = self.agentSocket.receive()
        parsed_stuff = parser.parse_sexp(msg)
        self.perception.process_vision(parsed_stuff, self.world)
        self.perception.process_gyros(parsed_stuff, self.nao)

        offset_for_player = -9 + (3*self.player_nr)

        self.agentSocket.enqueue(" ( beam -5 "+ str(offset_for_player) +" 270 ) ")
        #self.agentSocket.enqueue(" ( beam -1 0 270 ) ")
        self.agentSocket.flush()

        #Beispiel fuer laufen
        #Zielkoordinaten duerfen nicht 0 sein, sonst crash
        #Durch das drehen des sichtfeldes crashed ab und zu die
        #trigonometry funktion der perception klasse
        #siehe kommentare in der movement klasse fuer workaround
        #velocity und divergence kann in init angepasst werden (velocity immer < divergence)
        i = False
        while True:
            msg = self.agentSocket.receive()

            #logging.debug(msg)
            parsed_stuff = parser.parse_sexp(msg)

            self.perception.process_vision(parsed_stuff, self.world)
            self.perception.process_gyros(parsed_stuff, self.nao)


            #logging.debug('gyro rate: ' + str(self.nao._gyro_rate))
            #logging.debug('gyro state: ' + str(self.nao.get_gyro_state()))

            #lets the nao stand up from back
            # self.agentSocket.enqueue("( beam 0 0 0 )")

            #logging.debug('agent location: ' + str(self.world.get_entity_position('P' + str(self.player_nr))))
            #logging.debug('agent location: ' + str(self.nao.get_position()))
            #logging.debug('agent see vector: ' + str(self.nao.get_see_vector()))
            logging.debug('ball pos: ' + str(self.world.entity_from_identifier['B'].get_position()))
            
            if i : 
                m.run(-10,3)
            i = True
            # t.run_tactics()
            self.agentSocket.flush()

            # logging.debug(world.w.flags[0].get_position().x)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    try:
        agent_id = int(argv[1])
    except:
        print("You need to call \"./agent.py <player_id>\".")
        exit(1)

    Agent(agent_id)
