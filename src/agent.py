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
import communication
import signal
import sys
from sys import argv
import drawing
import __builtin__

# Hacky way to make global variables in Python
__builtin__.our_team = "DAI-Labor"
__builtin__.our_team_number = 1
__builtin__.number_of_players_per_team = 6



class Agent:

    def __init__(self,p_nr):
        self.player_nr = p_nr
        self.agentSocket = sock.Sock("localhost", 3100, our_team, self.player_nr)
        self.monitorSocket = sock.Sock("localhost", 3200, None, None)

        self.world = world.World(6, 30, 20)
        self.nao = nao.Nao(self.world, self.player_nr)
        self.perception = perception.Perception(self.player_nr, our_team)
        self.movement = movement.Movement(self.world, self.monitorSocket,self.player_nr)
       	self.keyFrameEngine = keyframe_engine.Keyframe_Engine(self.nao,self.agentSocket)
        self.communication = communication.Communication(self.agentSocket)
        self.tactics = tactics_main.TacticsMain(self.world,self.movement,self.nao)
        self.hearObj = None

    def start(self):
            self.monitorSocket.start()
            self.agentSocket.start()

            offset_for_player = -9 + (3*self.player_nr)
            self.agentSocket.enqueue(" ( beam -10 "+ str(offset_for_player) +" 0 ) ")
            self.agentSocket.flush()

            self.drawer = drawing.Drawing(0, 0)

            i = 0
            while True:
                msg = self.agentSocket.receive()
                parsed_msg = parser.parse_sexp(msg)
                while len(parsed_msg) != 0:
                    current_preceptor = parsed_msg.pop()
                    if current_preceptor[0] == 'HJ':
                        self.perception.process_joint_positions([current_preceptor], self.nao)
                    elif current_preceptor[0] == 'See':
                        self.perception.process_vision([current_preceptor],self.world)
                        # drawing some position as stored in world model:
                        player = self.world.entity_from_identifier['P_1_' + str(self.player_nr)]
                        self.drawer.drawCircle(player.get_position(), 0.2, 3, [200, 155, 100], "all.ownpos")
                        self.drawer.drawLine(player.get_position(), player.get_position() + world.Vector(player._see_vector[0], player._see_vector[1]), 3, [30, 255, 30], "all.see")
                        self.drawer.drawCircle(self.world.get_entity_position('B'), 0.2, 3, [255, 30, 30], "all.ballpos")
                        self.drawer.showDrawingsNamed("all")
                    elif current_preceptor [0] == 'GYR':
                        self.perception.process_gyros([current_preceptor], self.nao)
                    elif current_preceptor[0] == 'hear':
                        self.hearObj = self.communication.hear(current_preceptor)

                if not self.keyFrameEngine.working:
                    actions =  self.tactics.run_tactics(self.hearObj)
                    if i > 10:
                        for item in actions:
                            if item[0] == 'stand_up':
                                if item[1] == 'front':
                                    self.keyFrameEngine.stand_up_from_front()
                                    break
                                if item[1] == 'back':
                                    self.keyFrameEngine.stand_up_from_back()
                                    break
                            if item[0] == 'kick':
                                if item[1] == 1:
                                    self.keyFrameEngine.kick1()
                                else:
                                    pass
                            if item[0] == 'run':
                                if item[1] is False:
                                    self.movement.stop()
                                else:
                                    self.movement.run(item[1],item[2])
                            if item[0] == 'say':
                                pass
                            if item[0] == 'head':
                                if item[1] is True:
                                    self.keyFrameEngine.head_lookAround()
                                elif item[1] != False:
                                    self.keyFrameEngine.head_move(item[1])
                #a = raw_input('press enter:')
                self.keyFrameEngine.work()
                self.agentSocket.flush()
                self.monitorSocket.flush()

                i += 1



def signal_handler(signal, frame):
    print("Received SIGINT")
    print("Closing sockets and and terminating...")
    a.agentSocket.close()
    a.monitorSocket.close()
    sys.exit()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    try:
        agent_id = int(argv[1])
    except:
        print("You need to call \"./agent.py <player_id>\".")
        exit(1)

    global a
    a = Agent(agent_id)

    signal.signal(signal.SIGINT, signal_handler)

    a.start()
