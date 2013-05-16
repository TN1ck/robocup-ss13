#!/usr/bin/python
# -*- coding: utf-8 -*-

import sock
import parser
import world
import perception
import logging
import tactics_main
import movement


class Agent:
    def __init__(self):
        self.player_nr = 0 #TODO needs to be revised for multiple players

        self.world = world.World(6, 30, 20) # 6 players per team, field size: 30 meters x 20 meters

        self.perception = perception.Perception()

        #setup a socket-connection to the server
        self.socket = sock.Sock("localhost", 3100, "DAI-Labor", self.player_nr)
        self.start()

    def start(self):
        #start listening
        self.socket.start()

        m = movement.Movement(self.world, self.socket, self.player_nr)
        t = tactics_main.TacticsMain(self.world, m)

        self.socket.send("(beam -14 9 0)")

        #Beispiel laufen funktioniert nicht richtig!
        #msg = self.socket.receive()
        #parsed_stuff = parser.parse_sexp(msg)
        #self.perception.process_vision_perceptors(parsed_stuff, self.world, self.player_nr)
        #m.run(-1, 1)

        while True:
            msg = self.socket.receive()
            #logging.debug(msg)
            parsed_stuff = parser.parse_sexp(msg)
            self.perception.process_vision_perceptors(parsed_stuff, self.world, self.player_nr)

            logging.debug('agent location: ' + str(self.world.get_entity_position('P' + str(self.player_nr))))

            m.update()
            t.run_tactics()

            # self.socket.send("(beam "+str(x)+" "+str(y)+" 0)")
            # world.w.process_vision_perceptors(parsed)
            # logging.debug(world.w.flags[0].get_position().x)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    Agent()
